# Council Log

Chronicle of multi-model review councils: sessions where more than one
model reviews, counterreviews, or votes on JouleWise work before it
lands. Companion to `docs/decision_log.md` (which records WHAT was
decided about the system; this file records HOW cross-model review
reached it). One entry per council session; keep entries concise —
positions, votes, resolutions, and follow-ups, not transcripts.

Cross-session model-allocation evidence — which instrument (gpt-5.6-sol,
Opus 5, Fable, or the lead at the bench) should be assigned to which task
class, and what each layer has actually caught — lives in
`docs/process/model_allocation_ledger.md`. This file remains the ONE home
for per-session deliberation narrative; that ledger is the ONE home for
the structured, adjudicable allocation record.

Standing council roles (adopted C-001; process decision D-031):

- **Claude (lead/orchestrator)** — scopes work, diagnoses live/hardware
  failures, runs adversarial review workflows, owns bookkeeping and the
  final merge decision, and is the only member that touches real
  hardware.
- **Codex / gpt-5.5 (peer implementer-reviewer)** — implements against
  pinned specs, counterreviews findings on its own code, reverse-reviews
  Claude's commits and orchestration decisions, and is asked for design
  judgment explicitly ("argue the tradeoffs before you code").
- **Opus subagents (fast reviewers)** — parallel lower-level sweeps
  (commit hygiene, docs consistency, fixture audits) whose findings feed
  the discussion; cheap enough to run every session.

(Amended 2026-07-08: the Opus fast-reviewer tier was dropped at C-006
after zero unique catches; lead-driven pipelines are the default per
C-010; Ed granted standing self-merge-with-review authority in the C-010
addendum.)

Disagreements are discussed in at most one or two rounds; unresolved
disagreements are decided by the lead and recorded here with the
dissent. Anything user-facing (push/merge/publish) follows the user's
standing instructions.

## Index

| ID | Date | Topic | Outcome |
|---|---|---|---|
| C-001 | 2026-07-06 | Adopt review/counterreview between Claude and Codex (2H precedent) | adopted; all 10 findings accepted, Codex improved the blocker fix design |
| C-002 | 2026-07-07 | Reverse review of the 9-commit vertical-slice series; push vs PR | PR convention adopted; run_id renamed; P2-008 promoted; D-023 extended; sweep step added |
| C-003 | 2026-07-07 | Research agenda: what else can the instrument answer; robustness; scale-up | Q4-Q6 promoted; detection floor = methodology centerpiece; D-014 uncertainty found unimplemented; nodes/<node_id> flagged as pre-multi-node breaking fix |
| C-004 | 2026-07-07 | Difficulty-graded scored workload suites; collect-more-per-run | affine_mod_ladder_v1 adopted as ONE quarantined profile; rich-telemetry parsing (P2-009) prioritized ahead of it; examiner reframe adopted |
| C-005 | 2026-07-07 | Steelmanned research agenda + workload expansion | 31 tiered questions + kill list; jw_mixed_v1 starter suite specified (→ P2-012) |
| C-006 | 2026-07-07 | Session trace + orchestration meta-review of the six-stream parallel day | 13 attributed catches; integration-review step vindicated; skills deduplicated; operation-loop installed |
| C-007 | 2026-07-07 | Whole-project design/planning council (user-directed) + P2-013 fix design | P2-013 re-ranked above 2M with raw-to-trace gate added in-stream; two-claim-track framing adopted; detection floor gets an owning Phase 4 gate; machine-state queue lanes; pre-2M contract amendments (P2-014) |
| C-008 | 2026-07-07 | Multi-stream hardware-prep session (4 streams, Opus directors + Codex volume), user-checkpointed mid-flight | 3.0.1 verdict replay_supported; P2-013 groups 1-4 (19/31 pins); 2K protocol v1 provisional; DOC-007 done; Slice 2O landed; ledgers v2 + calibration + wake-gap lessons folded into skills same-session |
| C-009 | 2026-07-07 | META-REVIEW of the orchestration system itself (user-directed): 2 blind Codex analyses vs Fable's blind positions → conferral → SIGNED consensus | Hybrid topology + lead stream-state table; foreground-wait orchestrators + STALLED-handback; heartbeat demoted to backstop; Codex up-stack (design freedom, schema drafts, lead-decision packets); docs single-writer end-state (run report = session record; council log = deliberation only; RUN_STATE = pointer; ledgers retire at integration WITH branch/hash pointer); retired-artifact pointer rule; codex-run patch queued; preflight gates (device inventory, quiet lock, provisional labels) |
| C-010 | 2026-07-08 | Resume+merge session — first full run under the C-009 topology (pointer entry; full record in the resume-merge run report) | Lead-driven pipelines validated (zero stalls, no subagent directors); B-14/B-15 wire pins overturned by lens review pre-hardware; fabricated-evidence defect caught at lead diff gate (B-44); Ed grants standing self-merge-with-review authority; final-head review rule adopted; PRs #8/#9/#10/#11 merged |
| C-011 | 2026-07-08 | Counter-review of the independent project critique (4 verification lenses + 5.5-high adjudication; full entry below) | Critique findings adjudicated into mechanics: fail-closed campaign runner, counterbalanced order manifest, reducer honesty flags, claims ladder (D-037), P2-015 ranked before 2M; merged as PR #12 |
| C-012 | 2026-07-08 | Site observatory stream (pointer entry; full record in run report `2026-07-08-site-observatory.md`) — dual-prior design round, 2 image-critique rounds, visual sign-off, counterreview, final-head gate | Data-driven status frontend merged as PR #13; fail-closed parser honesty enforced (2 counterreview blockers fixed); P2-017 per-source stamps closed; image-heavy analysis routed to Codex as standing doctrine (Ed) |
| C-013 | 2026-07-08 | Lakebed deployment stream (pointer entry; full record in run report `2026-07-08-lakebed-deploy.md`) — 5.5 impl + 6 platform-constraint fix rounds + fresh counterreview | Site live as a shareable capsule with a live GitHub freshness layer (fails soft); lead owns deploy/claim (no sandbox network); site regen+redeploy folded into the RUN_STATE end-of-work loop |
| C-014 | 2026-07-08 | Workload-suite science hardening (full entry below) — lead audit + scout + 3 design lenses + invited peer counterreview | Q4-at-L3 gap closed via `q4_l3_shape_grid_v1` (4x3 + holdouts); P2-015 expanded to comparative MDE floors; jw_mixed common-shape stratum (C-W.1 was unfalsifiable); P2-010 split substrate/smoke, scored ladder deferred; two-quiet-window plan; analysis-plans contract (D-038); program restructure (D-039); two lead designs overturned by invited peer |
| C-015 | 2026-07-08 | Benchmark expansion council (full entry below) — reach lenses R1/R2 + design lenses E1/E2 + peer counterreview | Suite architecture v2 (D-040: B×k bundles, one generic mechanism, per-item status model); interop direction (D-041: HumanEval-first imports, marker-shim energy layer, kill list); capability map landed in bank; R2 collect-now set spawned the window-a-capture stream; capstone stop-line + D-034 gate restated |
| C-016 | 2026-07-08 | Post-large-workload meta-reassessment (pointer entry; records: D-043, `~/.claude/skills/skill-usage-log.md`, run report addendum) — 4 analysts (council/decision/skill mining + cold-start derivability) + completeness critic, Workflow-orchestrated | Supersession drift named as THE recurring unfolded failure mode (~70% of doc defects) → D-043 write-time + sweep-time discipline; operative merge-authority contradiction fixed; 5 skill divergences fixed; codex-delegation rewritten procedure-first; clean-machine derivability closed (scripts/codex-run committed + orchestration.md pointer map); §10 post-large-workload trigger now standing |
| C-020 | 2026-07-08 | STOP-AND-ANALYZE WHOLE PROJECT: technical + research merit debate (full entry below) — 69-agent Codex assessment workflow + 2 independent Fable position papers + recorded Fable-vs-Codex debate; owner-directed | Merit verdict recorded (docs/reviews/2026-07-08-technical-merit-review.md); D-048 model-first split program + D-049 transfer-boundary accounting promoted; question ranking adjudicated (Q4→Q1 coupled #1, Token-Shape Null sustained #2, Q6 elevated #3, affine ladder = validity instrument); crossover prior corrected by arithmetic; cheap-validity priority set (bundle publication + external re-reduction first); repo-verified gaps: bundles unpublished, no LICENSE, D-033 strict-validation legacy bypass |
| C-019 | 2026-07-08 | Post-suite-build meta-reassessment (full entry below) — 4 analyst lanes (5.5-direction study over 43 invocations; calibration longitudinal; project status/value ranking; closure) + completeness critic | Direction doctrine folded into codex-delegation skill (precedence/autonomy/FIX-N/production-gate clauses; model-version scoping rule pre-upgrade); D-013 prose back-annotated marker-bounded; shakedown gate added to P2-015; P2-025 adjacency + P1-008 elevation (incl. examiner acceptance-bar ask); pre-#21 corpus validity noted (dict-read-scale overhead, no re-reduction); watch items: integration-after-oversight, Opus A/B |
| C-018 | 2026-07-08 | D-013 alignment-capture window fix (parallel session; full entry below) | sampling_stopped stamped before alignment capture (PR #21: `255a7e6`, bookkeeping `c2e51b2`, merge `49c5b66`); suite 734; D-013 prose back-annotated to marker-bounded wording in the reassessment batch |
| C-017 | 2026-07-08 | Suite-build adjudication + implementation gates (full entry below) — Codex disposition draft + fresh adversarial round + lead calls; 11 unit lenses + 1 Opus outage substitute + 7-reviewer oversight + 3 final-head + integration | 37 amendments dispositioned → D-044..D-047; substrate/ladder/generators BUILT and merged (PRs #17/#18/#20/#19, suite 732); 3 lead live-only catches (refs, strict rollup, sampler namespace); oversight caught 2 validation holes pre-merge; PR #18 base-retarget slip recovered via #20 |
| C-021 | 2026-07-09 | Advisor status-site live-depth refresh (pointer entry; D-051; run report `2026-07-09-advisor-status-site.md`) | Static generated pages remain the audit fallback; Lakebed gets fail-soft live overlays from current GitHub markdown; Story page volatile counts removed; advisor cockpit expanded with attention, readiness, evidence, and claim-ceiling panels; gpt-5.5-high counterreview used before deploy |
| C-022 | 2026-07-09 | CP-5 resume session (pointer entry; run report `2026-07-09-cp5-resume.md` owns the full trace) — lead-driven, ~35 codex sessions: implementation, fix rounds, 12+ lenses/final-head passes, 2 integration reviews | PRs #22..#28 merged (merge-gate shape held: lens→fix→lead live gate→fresh final-head→CI→merge); final-head layer caught 3 blockers + 7 should-fixes post-lens; CI merge-ref caught the one cross-branch interaction (#23 fixtures × #27 strict rules) no other layer could see; 1 lead prompt-defect (inferred-sidecar pin) caught and refixed; methodology synthesis + suite_next packet adjudicated (CP-6); D-047 sampler clause amended (fail-closed); stop card CLEARED; Window-A GO |
| C-023 | 2026-07-09 | Scientific-rigor review of the measurement suite, benchmark, and full question bank (user-directed; full record `docs/reviews/2026-07-09-scientific-rigor-review.md`) — 4 fresh 5.5 lenses (metrology, benchmark/stats, per-question bank audit, advisor simulation) + independent lead read + 1 bidirectional discussion round | Verdict: strong provisional, advisor sign-off after a named all-software artifact list (error budget/P2-015 combined spec, analysis registry + multiplicity policy, canonical RQ registry + linter, frozen headline, contrast-level stats amendment, ordering executability, token-normalization contract); every blocker no-hardware-fixable; C5-1.1 blocker OVERTURNED in discussion (already contract-capped by C-014/D-037); ordering gap (C-015 promise vs manifest_order execution) elevated to pre-campaign; queue impact deferred to the step-2 planning session |
| C-024 | 2026-07-09 | Spec-fleshing wave 1 (pointer entry; run report `2026-07-09-spec-fleshing-wave1.md`) — 4 worktree streams (5.5 implement), 4 counterreview lenses, 3 fix rounds, 4 final-head + 1 tail-verification pass, integration review | PRs #29..#32 merged (D-052..D-055 ratified: scope contract, contrast-level stats + registry, false-effect guard floor, RQ registry); R2's estimator kill (percentile-UCB unidentifiable at n=10) was the session's decisive catch; integration review caught 5 cross-stream seam drifts (S1/S2 written against pre-S3 contract text); P2-015-PREP (queue rank 0) closed; checkpoint-push cadence adopted mid-session (Ed) |
| C-025 | 2026-07-09 | Wave 2 — ultracode workflow build (pointer entry; run report `2026-07-09-spec-fleshing-wave2.md`) — 46-agent workflow (4 impl streams, 8 lenses, severity-tiered refuters) + 2 lead-driven reinforcement streams + 6 final-heads + tail verification + combined-ref check + integration review | PRs #33..#38 merged (D-056..D-059 ratified: order policies + order_row, drift-is-a-bound + stable reason codes, token-normalization contract, claims-lint CI enforcement); refuter layer killed 10 findings pre-triage; final-heads caught 2 live-path defects (MLX position under rotation; linter false-negative regression); mutation testing debuted in the test-audit lens; combined-ref suite check validated the p2029 x p2030 strict-surface interaction pre-merge; suite 877 |
| C-026 | 2026-07-09 | P2-034 broad campaign packs (pointer entry; run report `2026-07-09-p2034-broad-packs.md`) — design-round-first (memo ratified w/ 3 pins), single worktree stream, dual lenses, final-head CLEAN | PR #39 merged; six packs, pack lint errors=0; compliance lens caught a char-level registry drift the linter cannot see (code-span nesting) + a scorer-leak + P2-022 structure flattening; executability lens caught the external-lab cold-start gap; pre-hardware campaign surface COMPLETE (every pre_hardware_preparable=fully row packed) |
| C-027 | 2026-07-09 | Whole-project council review with gpt-5.6-sol xhigh (first production session; 7 lenses: topdocs/rigor/stats/meta/reverse/arch/negspace + counterreview + independent Fable-tier final examiner; full record `docs/reviews/2026-07-09-c027-whole-project-review.md`) | 8 blocker clusters confirmed (token-denominator mislabel, superseded D-053 prose, RUN_STATE dual next-action, claim machinery unimplemented+unowned, empty D-050 manifest, four D-031 direct-to-main commits, evidence-integrity trio, protocol blockers); claim surfaces corrected same session; 14 follow-up queue rows + NV-GATE-2 additions to P2-005; D-060 proposed + D-061..D-063 accepted; counterreview reversed the lead twice (legacy-gate framing, restructure staging) |
| C-038 | 2026-07-25/26 | FLOOR-LABEL-01 gauntlet close (D-078 cl.11 labelled attribution-limited floors) + quiet-window collection; Ed re-proportioned the instrument mix mid-session (Opus 5 subagents = primary delegated lieutenant, Fable on genuine need, Sol = execution workhorse, lead adjudicates); full entry below | Opus-contract lens verdict COMPARATIVE COVERAGE: COMPLETE with 4 should-fix / 4 nits, incl. the `_combined_floor` key-sniffing misattribution mirrored bug-for-bug into `artifact.py` (so validation recomputes the same wrong answer and ships) and the ratio-unit floor/diagnostic inversion; Sol xhigh audit's 1 blocker (runnable V3 probe: comparative blocks minted WITHOUT admissible half-widths validate clean, floor_gate 5e-324 J vs 2.6484 J) ADJUDICATED DOWN to registered limitation L1 — first concrete demonstration of L1, and FLOOR-LABEL-01 recorded as modestly WIDENING its blast radius; Sol xhigh clock diagnosis root-caused window C to transient wall-vs-monotonic slew over the 5 ms ceiling (7.769 ms verified) and corrected the lead's duration hypothesis; Fable adjudication (zero tool uses, 108 s) OVERTURNED the lead's own self-diagnosis and named the disposition (rigorous on work products, exempts its own premises about the environment) → rules R1/R2/R3, no demotion; window B 59/59 clean (whole-window verdict PENDING), window C failed twice on clock slew, window D not started; FIVE lead errors recorded, incl. the ~10-hour lost quiet window (untracked `nohup` + turn ended with no wake source) and TWO exit-status masking incidents → generalization: EXIT STATUS IS NOT EVIDENCE OF WORK DONE |
| C-040 | 2026-08-01/02 | Commit-3 cooldown-join gauntlet: five fix rounds and three cold-gate dispositions | PR #93 merged after the custody micro-commit and exact-set pin; D-105 recorded the residual recognizer boundary; every review layer produced unique catches |
| C-041 | 2026-08-03 | D100-BII nested-closure arc and CAL-BRACKET design consult | Three closure formulations failed and the bench loop stopped for decision-level rulings; CAL-BRACKET F3 escalated; MINT-GENERALIZE tooling merged |
| C-042 | 2026-08-03 | Ed-requested pre-ruling debate: 2-round adversarial Sol xhigh consult over the D-108/D-109 decision packets (MCP discussion lane, read-only; Sol instructed to bench-verify packet claims; record .desk/2026-08-03-sol-debate-d108-d109.md); Ed then ruled by explicit deferral to the joint position | Both packets materially changed before ruling: Sol caught the overstated three-subject manual-verification claim and broke the original A-min formulation (writer crash-window; prefix-subset is not anti-rollback) — both lead-verified and adopted (reservation-first + repo-committed head pin now D-109 law); Sol's code refutation of the magistrate's two-subject license-surface counter adopted into D-108 clause 2; magistrate context (schedule slack, metrology pivot, shared-R2 marginal cost) flipped Sol's B recommendation to A-min-with-reservation, withdrawn on the record; residual dissents preserved in both decision texts |
| C-043 | 2026-07-22 | D-078 P0 instrument-repair close-out (round-8/8b landing + §C-028 delta re-audit with 3 lenses / 11 refuter runs, round-9 FINAL confirmation, L1 adjudication, PR #79) | Round-8b delta re-audit caught the understated-B_fiducial ClockStamp blocker two audited rounds missed; refuters killed 2 findings, narrowed 1, split 1 (lead-synthesized); CR9-1 adjudicated as registered limitation L1 + FLOOR-BIND-01; failure modes recorded (content-filter refuter kills -> data-quality rephrase; bench-edit-during-enforced-scope false attribution; review-genre null-final recovery) |
| C-044 | 2026-07-24 | NEG-8 drift-gate estimand debate (Ed-directed pre-ratification cross-model debate; Sol xhigh peer vs lead ruling) | Peer disagreed on inferential role (screen != stability proof) and was adjudicated CORRECT; Ed ratified the amended screen+budget design (option F full) with rigor-spiral + no-invented-physics guardrails; second recorded case of peer design judgment overturning a lead ruling pre-implementation |
| C-045 | 2026-07-24/25 | NEG-8 SCREEN+BUDGET audit gauntlet: four audit rounds and paired contract/execution refuters | PR #85 merged after three fix rounds; the paired lenses materially changed triage, and the residual custody-hardening work was queued |
| C-046 | 2026-07-26 | Retrospective: CAL-REBRACKET-01 max-bracket consumption gauntlet (PR #86) | Governed consumption-time authenticated re-derivation landed after three implementation rounds and three independent audits; a9/a10 replays passed with widened members and unchanged point estimates |
| C-047 | 2026-08-03 | The 16h runway (Ed-granted; joint Fable+Sol decision authority; concurrent sweep instance mid-flight): D-108/D-109 debate+rulings executed, D-110/D-111 sweep-triggered rulings, winB STOP cold gate -> D-112, two Sol gauntlets, pinned byte-identical mint replay, checkpoint for harness switch | D-108 closed via PR #99 + re-record; CAL-BRACKET held at 2e61ff9 (B1 residual, rule-11 gate owed); winB license exhausted as drawn (r06 disposition parked for Ed); mint chain D-110-blocked; CLAIMS_STATUS section 1 honestly NONE; sweep propagation fixes landed; layer yield in the run report |
| C-048 | 2026-08-04 | Integration-collision resolution on the CAL-BRACKET-D079-01 lead gate: bounded pre-decision Sol HIGH consult -> consult-shaped signature amendment -> fresh delta re-audit -> bench guard hardening -> merge-ref CI | The delta re-audit PROVED a live repr-'None' default spoof against the rendered-signature guard (hardened with a regression); the consult corrected the byte-identity oracle to integration-tree core-vs-wrapper parity (a historical-digest replay would have contradicted D-110); lead integration-tree replay 2487 OK exit-0 unpiped; PR #100 gate-complete, merged 2026-08-05 (`f75d12b`) |
| C-049 | 2026-08-05/06 | The 12h autonomous marathon: six PRs (#102-#104, #106-#108) + PR #109 issuance gauntlet; two rule-11 escalation consults (CGV F3 closure, QG census Option C); the D-079 issuance cold gate (split verdict, HOLD upheld); D-113/D-115/D-116; then the first re-mint consumption attempt exposed a structural closure -> Sol xhigh fork consult | The cold gate's HOLD prevented an irreversible ledger write paired with a production-refused artifact (F1 no-consumer-path, F2 digest-role coupling — issuance reframed as implementation and re-gauntleted as PRs #108/#109); xhigh delta re-audits again caught introduced defects (QG init-durability F1; CGV live-proved receipt-serialization B1 + phantom-fence B2); historical max-bracket consumption proved structurally closed at main — Option 2 (three fresh prospective windows) recommended by consult + magistrate; Ed's ruling OWED at close |
| C-050b | 2026-08-07/08 | The evening double-window: PR #114 re-gate + merge; U1 split -> PR #115 (paired lenses, convergent P1, bench fix, full 11-item ledger) merged; two escalation consults ADOPTED (ledger-resident recovery shape; U5-U7 launch contract); U2 cold gate convened -> NOT RATIFIED, packet remanded; trust + reasoncode gauntlets; PR #116 merged as the FIRST full D-121 gate; D-120/D-121 minted | Layer catches: Sol delta found the one-sided session-endpoint P1 the original gate-debt delta missed (Opus counter-review converged independently — the paired-lens design proven); the Opus U2 refuter found the packet quoted the WRONG authority set (D-109 omitted, operative for 7/12 questions) — a defect the cold judge structurally could not see; Opus trust counter-review caught the branch FALSIFYING a paper sentence (cross-surface, context-dependent); Sol trust audit ruled same-signature YES round 1 (binding chooses its own window) -> fix round 2 with the escalation tripwire armed; recovery round 1 NEEDS_SCOPE surfaced the receipt-cadence doubling as a design consequence needing a ruling, not a patch; magistrate bench: golden fixture-review method (reverse-transform must reproduce old hashes before adopting new), two lead errors closed structurally (repo-cwd reviewer detached main; piped-replay recurrence) |
| C-050 | 2026-08-07 | Paper-first session under Ed's Sol-burn license: the MVP capstone paper through a full round-2 gauntlet (2 lenses → bibliography/novelty audit → Sol xhigh fix round → delta re-audit → bench fidelity corrections) + D-117 transcription + plan-freeze ratification + night-hardening 3-lens sweep + a 24-direction paper-portfolio factory (Sol fast proposals → Opus 5 referees → dual opposing-prior Sol xhigh syntheses → magistrate adjudication) + U1/U3 implementation gauntlets + read-only meta-sweeps and a far-ahead plan factory | Paper SHIPPED as a complete draft (PR #110 merged, `6a70707`); D-117 + the plan-freeze design memo ratified (gates 1-8, work orders U1-U10); portfolio arc adopted (MVP + Window C → quantization BF16/Q4/Q8 → MoE stretch) with 7 night-cheap riders folded in; the PAIRED AUDIT LENSES were the session's highest-yield layer by a wide margin (U3 contract lens live-proved that fabricated custody hashes plus tampered drift/allowance still minted the four-cell artifact; U1 execution lens live-proved concurrent double-arm acceptance and a "never leak" test that asserts the leak); the delta re-audit again caught an INTRODUCED blocker (recovery boundary, 7/8 closed) and the Opus referee corps caught a portfolio-wide ~5 J-vs-~14 J floor-sizing error, the Window-C/§6 evidence gap, and the paper's missing advisor-lineage citations; U1/U3 branches pushed awaiting final gates; Ed's rulings ##1-7 OWED |
| C-051 | 2026-08-08 | T0 window session under D-128 (morning → ~13:40, ended by Ed's stop order): three Phase A streams — trust round 2 (7-step ruled sequence), recovery gauntlet + FIX-1..13, U2 attestation rework — plus the results-prose merge (`1e6fa16`, class dead after 4 deltas); trust banked UNGATED at `1cae2bc` on a mid-run kill at ~4h22m; recovery banked UNGATED at `468e0a6` (delta owed with 3 questions); U2 FROZEN at attestation count 3; D-126/D-127/D-128 minted; trust F1/F2 (`fe85b09`) + recovery witness-scope (`6981d2b`) rulings custodied | Escalation discipline held 3-for-3 (trust delta classes at count 2 → consult; recovery ungoverned-refusal at count 2 → exit-completeness consult; U2 attestation at count 3 → freeze + cold-gate packet — no round-3 fix anywhere); gauntlet lenses A/B both FAILED the recovery round-3 corpus with reproduced production defects (fix-rounds-introduce-defects doctrine held again); the U2 delta executed a live forgery — a ledger-absent epoch accepted as `VerifiedAcceptance` through auto-enrolled always-true verifiers — the Potemkin catch that ended the stream; the trust F1/F2 consult out-designed both magistrate proposals (A→B→A TOCTOU proof killed boundary hashing; content-addressed custody store over the relocation table) and was ADOPTED IN FULL; magistrate bench caught the recovery harness's own 8-orphan SIGKILL leak (routed to the successor delta per the two-writers rule, not injected live) and the ~3.1GB fixture push blocker (substrate ruling opened); mid-run kill adjudicated as bank-with-written-trust-nothing-rider; entry successor-written (dictated-fills), spend snapshot not captured |
| C-052 | 2026-08-08 | T1 Phase-A continuation under D-128: fixture-substrate ruling (`8788891`/`b7aad49`); Codex Fast Mode standing default (`de759c9`); recovery delta-1 → ESC-2 → FIX-14..18 → six-lens count-3 freeze → two-instance cold gate → adopted discharge path (`721593b`, `bc01908`, `4495609`, `0c30993`, `e265c9c`); trust 2b eight-hour wall + recovered partial proof and 2c verification tail with no captured report (`trust2b-out.manifest.jsonl`, `trust2b-report-recovery.md`, `trust2c-out.manifest.jsonl`) | Substrate consult out-designed the listed storage options and release hydration was adopted; fast became Codex's standing default with an explicit opt-out; recovery's freeze was confirmed, FIX-19 AST hardening prohibited, ARMING made conditionally dischargeable through a G2/G4/G6 executed-probe round + manual arming + lead live verification, while witness integrity moved to an off-path mutation-kill harness; trust 2b proved selected core/mint stages but failed the decisive regression and never reached v1 parity/full suite, while all 2c proof outcomes remain UNVERIFIED because report capture failed. Per-layer catches were non-overlapping: delta-1 caught recurring under-proof; ESC-2 supplied terminating designs; delta-2's six lenses each returned NOT-CLOSED; Opus caught the G2 label contradiction/core-seam dissent; cold Fable caught the unattainable in-process property; the lead honored classifier denial and Ed reset fast/parallelism policy. (Evidence: `trace-notes.md` lines 39–194; `e265c9c` synthesis; trust manifest line 2 records.) |
| C-053 | 2026-08-08/09 | T2 window session (~23:30 → ~08:30 Ed checkpoint): five PRs merged — #117 packs (unfrozen drafts), #118 recovery/arming code + §5C procedure, #119 operator arm-readiness, #120 results scaffold, #121 methods+draft — plus suite repair `55a05e3`, prose-linter 3.11 fix `b3a5008`, T1 bookkeeping `01420da`; trust mint bar PROVEN (all 15 attack domains refused; 11 stale fragments vs 1 real coverage shadow triaged, shadow reworked + isolated-proven) with landing deliberately deferred at hour nine — clean-branch resynthesis method adopted over the insufficient amend procedure, nine-site trust×recovery seam discovered and R1 security-adjudicated (3 auth-routed reads, 6 line-anchored exemptions); pack-freeze plan fully ruled incl. Ed's Q1 (p256 prompt, token-ID SHA `83099a66`) + Q8 (dedicated p256 floor cells) taps and the "better paper" tiebreaker; flake fix banked `5a8a200` | Layer catches: Sol counter-review corrected all six substantive errors in the lead-authored §5C arming procedure; trust triage preserved the one real category-B coverage shadow (`primary` refused by evaluation-basis validation before the intended `bundle_sha256` discriminator) instead of blanket-accepting twelve fragment failures; landing design caught the recorded amend procedure retaining the 3.3GB content ancestry BEFORE execution; conflict review + R1 resolved the nine-site registration-at-read seam with zero broad exemptions; the pack review wave found parallel-authoring schema/vocabulary divergence and its refuter layer killed five plausible false findings; U7's implementer NEEDS_RULING'd a decode-only instruction contradicting ratified D-122; lead fleet check avoided killing CPU-active mint children behind idle unittest parents; the hour-nine deferral kept proof and integration as separate gates rather than rushing a security classification |
| C-054 | 2026-08-09 | T3 window session (~08:30 → 21:35 Ed wrap; first session under D-129, ~9 concurrent streams): PR #123 flake fix merged `cace694` after a lead 8/8 verification loop; T2 bookkeeping `7fde68b` + council-index parity repair `966dd39`; WO-4/Q9 prefill phase-recording proof DISCHARGED `2cd9bc3` (7B PROVEN 50/50 identifiable, 1.5B PROVEN-WITH-CAVEATS on 37/50 `not_resolvable_sample_count`, 0.0 J max reintegration discrepancy both stacks); extension-axes H1/H2 roadmap DRAFT `e9c2433` (18-row ladder, nothing registered, D-075 authority with Ed); site-renderer silent 64KiB truncation FIXED `955df9b`; consistency sweep + D-129 (fan-out standing order, ~60% fast-tier cut, Fable-economy-with-full-coverage) + state-kernel gate → T3 `50d1064`; release `fixture-d117-v2-production-v1` published and digest re-verified; trust PR #122 driven to `e871f5b` with the 16-question delta 16/16 and BOTH decisive-CI rounds root-caused and fixed, decisive run still in flight at wrap; WO-2 PR #124 opened `f7117e1`; FLOOR-COMMONMODE-01 banked UNGATED `425f75f` (audit + D-118 gauntlet owed); WO-3 not started | Layer catches: the 16Q Opus grader/refuter fleet found the guard blind to readable `os.fdopen` (Q10 blocker) and falsified a T2-magistrate-APPROVED classification — `open_append_descriptor`'s "append handle" justification contradicted by its own callers (Q3); the Q10/Q3 RE-GRADE residuals then found two latent holes the findings themselves had missed (`io.open`/`codecs.open` misparsed with the path read as the mode, so `io.open('led.bin','rb')` passed unseen; the `fdopen` fail-closed default pinned by no test); read-only Sol diagnosis proved decisive round 1 was LATENT not merge-introduced — T2's green local runs had silently read Ed's machine-local/iCloud paths, and hiding only those paths reproduced the CI refusal on both interpreters; the round-1 fix's OWN new hermeticity assertion then caught a second unplumbed read site in downstream candidate rediscovery (`calibration_bracketing.py:961`), and census evidence (38 content IDs × 5 governed artifacts + 20 builder-added members) made narrowing it indefensible — production fixed instead, forbidden locator set untouched; CI's 3.11 leg exposed a 1-ULP `builtins.sum` divergence against the exact-golden extraction report while 3.13/3.14 stayed green; the site-lane test turned a silent rc=0 mid-byte truncation into a deterministic `UnicodeDecodeError` once decision-log growth crossed the 64KiB pipe buffer (pipe 65,536 B vs file 510,214 B); the site build's heading↔index parity check caught the C-053 row the T2 bookkeeping commit omitted; the consistency sweep found 22 stale operative statements in 7 of 9 docs incl. the pack-freeze pre-tap wording C-053 had flagged and left open; WO-4's mislabeling discriminator separated a sampling-cadence limitation from boundary mislabeling and turned it into a forward warning for the Q8 p256 1.5B cells; three Sol envelopes returned blocked/partial immediately on the F3 read-only-sandbox launcher trap rather than fabricating progress |
| C-055 | 2026-08-10/11 | T4 window session (~14:09 → 20:54 PT; the mint bar LIFTS): trust PR #122 MERGED `ae6af48` at head `e871f5b` after the `d117-production-proof` decisive job was cancelled TWICE at the exact 360-min hosted cap — standing escalation trigger + verdict-authority reinterpretation both routed to a COLD GATE, which re-seated decisive authority to the custodied lead local execution (12,938.543 s, rc=0, CI-identical hydration) taken with the CI-proven steps 1-7 chain; **D-130** minted (substance over venue, fenced to PR #122, five-part substitution test, expiry at WO-CI-RESTRUCTURE, citation discipline); post-merge batch `654c53d` (evidence bundle committed, workflow de-triggered to dispatch, replay recipe `scripts/replay_d117_decisive.sh`, two "required"-wording contract sentences amended, work order registered); kernel UNGATED + fidelity pins cleared `b04c5bf`; WO-2 `#124` and WO-3 `#125` MERGED (replay-derived receipt oracles, 10 rows / 5 logical ops); FLOOR-COMMONMODE-01 **FROZEN** `123e8a5` after five understatement mechanisms across four fix rounds, four delta audits, one escalation consult and THREE cold-gate sittings (terminal FCM-R4-01, 5.0e-10 J exact at admitted inputs; production path unaffected; Ed decision packet); paper Rivoire-bar program (5 lenses → 5 trains + 3 figures) opened as PR `#126`; freeze-plan lineage-monotone addendum `51bcf77`; arm-packet skeleton with 12 recorded arming-surface discrepancies | Layer catches: the trust COLD GATE vacated the project's own designated decisive venue as physically unsatisfiable and re-seated authority on evidence — reversing the magistrate's standing position — while its paired contract-lens refuter produced the session's sharpest finding, that the local run's legacy-locator assertion executed against **190 LIVE machine-local decoy paths** (38 committed ledger locators × 5 governed artifacts, the exact T2 iCloud leakage paths, verified still present), making the local green hermetic-BY-CONSTRUCTION and STRONGER on operator leakage than a hosted run where those paths do not exist — and it refused to overclaim, leaving three residual holes on the record incl. "do not cite [the bidirectional audit leg] as hermeticity evidence" and finding `main` unprotected so "required" has no mechanical backstop; the FCM gauntlet's two DISTINCT lenses each found what the other could not (execution lens executed 0.25 J vs a 0.50 J dense-grid width with equal control cases bounding it to non-contiguous geometry; contract lens proved that geometry PRODUCTION-REACHABLE through cumulative-float support construction no upstream gate rejects) and each killed its own plausible hypotheses (Q-B refuted, P-3 refuted, P-4 downgraded); the escalation consult located the flaw INSIDE the registered identity (the parameter dict pinned `shared_extrema_rule=separable…`) and returned a terminating design, adopted in full; the four delta auditors escalated strictly, each finding a mechanism the weaker prior audit could not see (1.06 J separable-composition collapse → 2.3e-13 J enclosure defeated by cancellation → 1.0e-9 J zero-point tolerance/identity conflation PRE-EXISTING in the original bank → 5.0e-10 J unauthenticated zero-point found by a FRESH auditor), with delta-3 explaining why round 3's own oracle was structurally blind to it; the Sol implementer returned `needs_ruling` against the COLD GATE's own dictated acceptance bar (algebraically inconsistent, 61/64 exact cases failed) and its resolution was adopted verbatim; sitting 3's oracle-authorship separation proved load-bearing (refuter-authored oracle committed BEFORE implementation, byte-verified untouched; the refuted candidate fails 16 assertions under BAR 1 "where BAR 2 alone would ship it") as did real-fixture-first ("every oracle in rounds 0-3 was synthetic in exactly the dimension that hid the defect"); the WO-3 refuter refuted 3 of 5 questions with executed probes and confirmed the `+10` terminal-sequence rule excludes valid recovery control rows (torn-target probe: 11-row refusal-free finalized session); the paper metrology lens falsified a floor guarantee BY COUNTEREXAMPLE (n=10: floor 0.9 J vs largest member half-width 1.0 J) and its F6 propagated OUT of the paper into a runbook-vs-code correction on main `4d3e3ad`; the web lens found five advisor-visible S1 defects (fabricated SPEC URL suffix+date, clock-sync misattributed to SPEC not MLPerf Power, a rigor property credited to a paper that never defines it, two wrong author initials, a missing same-hardware Apple-silicon paper); the terms lens caught the paper forbidding a summed acceptance threshold and then evaluating against exactly that sum; the magistrate's own final linear read caught two numbering defects that survived all five lenses and five trains (figures numbered by filename not order of appearance; "Table 1" used twice) and diagnosed the `ci` shard-4 failure as a load flake (2,036 s vs ~650 s) rather than a defect; PROCESS: delta-2 COMPUTED an exact-arithmetic understatement verdict and dropped it from its report (float keys only), so a verdict of the class that later became dispositive never reached the adjudicator — the episode's highest-value finding |
| C-056 | 2026-08-11 | T4-late adjudication chain (~01:05 → 15:56 PT, continuing after C-055 landed): FLOOR-COMMONMODE-01 STOPPED on its round-5 delta (FCM-R5-01, 4.999917146975008e-10 J exact via generated-constructor/`replace`/`__new__`/copy/pickle fabrication) `0b5fce8`, REVIVED by **D-132** (Ed: stopping rules target doom loops, not converging instruments) as round 6 `3390cb7` deleting the public registered surface, then REJECTED by its fresh delta on **FCM6-01** — the registration dictionary injected into admitted JSON passes both validators AND `authenticate_floor_artifact_bytes`; the mandated COLD GATE (fresh Fable adjudicator + paired Opus contract-lens refuter) ruled **D-133** `f0e7cf6`: fallback `respec/d124-withdrawn` merges after its own gate and the freeze lane DECOUPLES from FCM-01, FCM-01 continues unmerged under **ALT-D120** (delete the serialized vocabulary per the D-120 precedent, don't authenticate it), a full fresh delta owed with permanent-drop terminality, re-spec-back conditional on three items incl. the newly registered WO-MINT-ESTIMATOR-VOCAB; rounds 7 `e29a062`, 8 `4f04100` and 9 (in flight) followed, canonical suite 3,018 OK; U11 identity-pin projection ran four fix rounds to a clean fourth delta; calexits fix round 3 `1e96f96` + round-3 audit appended to WO-SAMPLER-SUPERVISOR `96b20ae`; paper train F `#128` and arming-surface fixes `#130` MERGED; PRs #127/#129/#131/#132 all open | Layer catches: the round-6 delta reached the **serialization boundary**, a class no prior round touched, executing both forgeries (parameter sha `dea20dc0…` authenticated at forged artifact sha `8afdcb51…`) and proving the “closes by construction” claim false at committed validators; the cold gate's paired **Opus refuter supplied every decisive input** — mint scripts contain ZERO estimator vocabulary, the forged field is CONSUMER-INERT, and the production claim path binds `expected_sha256` which the delta's reproduction omitted — plus ALT-D120 and the freeze-decoupling hybrid, all bench-verified before the revised sitting, at which the **fresh Fable adjudicator WITHDREW its own first ruling**; the O3 full delta cleared the arithmetic TERMINALLY (4,096 exact-rational cases, zero understatements) and STILL found **FCM7-01** (13 nested mapping paths; duplicate-key JSON where `json.loads` keeps the last while authentication binds the bytes), the round-8 delta went narrower to a **legacy plain-`json` loader**, and round 9's mandatory census fired NEEDS_SCOPE on two analysis-engine modules — each layer strictly narrower than the last; U11's third delta **walked around the magistrate's own one-line bench fix** `3657f4d` with a non-numeric `projection-000a.json` (fix correct, regression biting, allowlist shape still wrong) — the day's sharpest layer justification; **rule 1 held again**: full hosted green, lead live verification RED twice (`KeyError: 'code'`, ~24 orphaned `fake_sampler.py` processes — CI's own cleanliness was hiding it), the round-3 audit then finding the killed-interpreter writer-stranding class; PROCESS: four Sol runs died at exactly 902 s with no report — `codex-run-v3`'s default `--timeout 900`, not the read-only sandbox, was the true systemic killer |
| C-057 | 2026-08-11/12 | T5 window session (~20:35 PT 08-11 → ~10:45 PT 08-12 Ed stop order; Ed's 12h autonomous window): the T4-late merge queue cleared **6/6** — PRs #132, #133, #131, #127, #134, #129 — plus three same-session PRs opened, gated and merged (#136 D-135 advisory site budgets, #137 p2038 clock-phase flake, #139 calexits mutation classifier), **ten merges** in all (#138 Q8 p256 floor cells landed after this entry was drafted); **D-136** minted on main (Ed: the site lane is retired from all automatic processes, `f4aa138`); the WO-MINT-ESTIMATOR-VOCAB **COLD GATE** sat and custodied its full record for the first time (`docs/process_traces/2026-08-12-mintvocab-coldgate/`: packet + three rulings) — option A authorized under a self-contained F1–F12; the §5C arm-readiness generator (D-134) ran a three-lens gauntlet at `3a140bb`, a fix round, a FIX-1 delta re-audit, a bench repair and an integration tree; two PRs open at stop (#135 crash-matrix exclusive, #140 mintvocab gate-complete) | Layer catches: the cold gate's **paired** reader is the entry's headline — the fresh Fable adjudicator found the binding-seam fail-open that both prior condition sets would have certified as closed, and its paired Opus contract-lens refuter then proved the adjudicator's own cure **INERT** (v2 forces one `evidence_root_id`, so the absolute and comparative refusal messages are byte-identical and the suffix match closes nothing) and restated C1 against a main that had moved under the packet (`bf628eed…` → `79229aa2…` at `14879e4`); ruling-3 records that *neither* the provisional five *nor* ruling-1's C1–C10 would have caught it; the attestation layer then caught **B1** — `test_common_mode_full_cli_path_writes_bound_exact_artifact` replaces the pinned binder with a stub returning `{}`, so its name claims a binder-verified full mint it never performs — and flagged **G3**, the decision-log's "terminally clean" FCM record standing against an authority that directs D-133 cl.3 be reported open; on §5C, lens A executed a **live** derive-never-enter forgery (operator-attested evidence → `validator_status=PASS` with `operator_source=OPERATOR_ATTESTATION`), lens C found 7 documentation blockers, lens B's mutation census killed 21 of 25 with 4 regression gaps, and the FIX-1 delta then found **2 of 35** predicate transcriptions WEAKER than contract — both on rows that mix live T-0 facts with frozen pack facts; the bench repair of those two exposed **nine** end-to-end/integration fixtures that had been minting reservation receipts bound to nothing, passing only because the code was exactly as weak as the fixture (D-132 guard held the occurrence count at TWO — converging instrument, not doom loop); the **integration tree** caught what no branch could — the doctrine branch minted a second **D-136** from a base predating main's, and its own "exactly one D-136" proof was correct in-branch (`5a80e39`); direction-layer: an unfilled `[LEAD FILLS THIS SLOT BEFORE LAUNCH]` returned `needs_ruling` instead of invented shipped behavior, the docs branch asserted reboot-fence machine behavior ~45 min before the code that enforces it was committed, and requiring exact `file:line` from every lens turned doctrine triage into grep (two FIX-E targets found MISSED); infrastructure: four Sol runs died at 59.8–60.0 min against a subagent-shell kill cap, one of them mid-canonical-suite |

---

## C-001: Review/counterreview adopted (Slice 2H)

- Date: 2026-07-06. Participants: Claude (lead), Codex gpt-5.5 (author +
  counterreviewer), 22 review/verification subagents.
- Shape: Codex implemented 2H → Claude live-verified → a three-lens
  adversarial review workflow (contract / correctness / test-adequacy;
  every finding survived an independent refutation attempt) confirmed
  10 findings (1 blocker, 6 should-fix, 3 nits) and refuted 2 → Codex
  counterreviewed as a peer.
- Votes/positions: Codex accepted all 10 findings (refuted none) and,
  invited to argue design before coding, proposed a better blocker fix
  than either option the lead posed (`AdapterFailure` structured
  exception; controller maps the true `FailureReason`).
- Resolution: all fixes applied; suite 251 green; live re-verified
  (fail-fast at idle_baseline, `permission_denied`, no fabricated
  baseline). Precedent: green tests are necessary, never sufficient —
  the blocker was invisible to a fully green suite.
(Amended 2026-07-08: the Opus-refuter tier was dropped at C-006 after
zero unique catches; refutation-as-protocol lives on with fresh Codex
refuters, as recorded in the adversarial-review evolution.)

## C-002: Reverse review of the vertical-slice series; push vs PR

- Date: 2026-07-07. Participants: Claude (lead), Codex gpt-5.5 (reverse
  reviewer of Claude's commits AND decisions), 2 Opus subagents (commit
  hygiene; docs consistency).
- Subject: the 9 unpushed commits (`10a570d`..`123d87a`) and five of
  Claude's orchestration decisions (flagship config mutation, 20 Hz mock
  workaround, provisional D-016 wording, main-branch convention,
  bookkeeping fidelity).
- Findings that survived: (1) stale gate-state prose in 6 files
  (Opus sweep + Codex independently convergent) — README/playbook test
  counts, phase-1 sudoers rows, phase-2 status paragraph contradicting
  its own matrix, PROJECT_STATUS blocked-items, wrong skip count, stale
  CI run number; (2) Codex-unique: the flagship config kept run_id
  `example-mac-mlx-local` across a workload-semantics change — explicit
  run_ids bypass hash suffixing, blurring provenance; (3) both reviewers
  independently: the committed sudoers line exposed the OS username.
  Commit hygiene otherwise CLEAN (messages match diffs, test-count chain
  reconciles, fixture justified, no secrets); CI risk assessed low
  (Codex ran the suite, config validation, and mock e2e itself).
- Discussion round (positions → resolution):
  - D1 flagship mutability: Claude held configs are entrypoints (run
    identity = config hash, D-022/D-029) but conceded the run_id rename
    (`example-mac-mlx-local-512t`); Codex concurred and withdrew the
    separate-config ask ("a committed known-unmeasurable config is a
    footgun"); the short-window finding lives in the 2I run report.
  - D2 P2-008 urgency: consensus rank 3 with a hard "before 2K/2L
    bring-up" gate (mock telemetry under SystemClock is now real-runtime
    test infrastructure); not above 2M/Stage 3.0, which don't touch the
    edge.
  - D3 bookkeeping drift (structural): consensus two-part fix — D-023
    extension (prose status summaries carry an as-of date and defer to
    checklist matrix rows; no re-narrated gate lists) + a standing
    end-of-session docs-consistency sweep by a fast subagent
    (RUN_STATE end-of-work step 7). This session is the proof: the sweep
    caught everything the peer reviewer caught.
  - Push vs PR: Codex recommended branch+PR (one GitHub-readable diff +
    CI before main for a mixed code/config/docs series); Claude accepted;
    unanimous. Convention adopted for multi-commit sessions (D-031).
- Pre-PR blockers (all applied in the fix-up commit): staleness fixes,
  run_id rename + hash pin, `<local_user>` genericization of the sudoers
  line in docs, this log, queue re-rank.
- Dissents: none outstanding.
- Follow-up (user direction, same day): next multi-stream batch
  (2M / P2-008 / kv-size) runs as parallel worktree streams, each owned
  by a Fable orchestrator subagent driving its own Codex thread, landing
  as separate PRs (D-031 execution-topology addendum).

## C-003: Research agenda expansion (ideation council)

- Date: 2026-07-07. Participants: Claude (lead), Codex gpt-5.5 (ideation +
  critique), 3 Opus subagents (RQ-from-instrument; collection feasibility;
  robustness + scale-up).
- Key outputs: Codex's fixed-vs-marginal energy model (adopted as Q4;
  subsumes prefill exponent) and compositional split prediction (folded
  into Q1's method); ranking stability (Q5); boundary sensitivity (Q6).
  Opus ground truth: detection floor (idle stddev 5.4 W > mean 3.5 W),
  ~30-75 bundles/hour throughput with automation (not schema) as the
  campaign blocker, `SummaryMetrics.uncertainty` is a documented-but-DEAD
  field (D-014 never implemented), and the composite bundle layout
  hardcodes `nodes/prefill|decode` — a breaking generalization
  (`nodes/<node_id>`) required BEFORE any multi-node data.
- Dissent adjudicated: Codex voted to cut "variance" as an RQ
  (methodology, not science); lead partially conceded — it became the
  methodology centerpiece (detection floor) rather than a numbered RQ.
- Resolutions: promote Q4-Q6; queue D-014 implementation as the highest
  credibility-per-hour item; question bank doc created.

## C-004: Scored difficulty suites + per-run collection expansion

- Date: 2026-07-07. Participants: Claude (lead), Codex gpt-5.5 (3 parallel
  read-only ideation threads: suite design / collect-more / examiner,
  plus a synthesis-review round), 1 Opus subagent (plist ground-truth
  audit).
- The examiner thread argued the naive difficulty-vs-energy claim
  collapses into token count for dense models and correctness scoring
  drifts into Intelligence per Watt's lane; the design thread's
  `affine_mod_ladder_v1` (difficulty = iteration count, prompt shape and
  answer length FIXED) survives the attack by construction — the claim
  becomes energy-per-CORRECT-answer under a controlled energy envelope.
  Synthesis-review round added the final caveat: record per-item token
  count/stop reason/malformed status and verify wrong answers are not
  systematically cheaper (early-EOS bias would understate the curve).
- Ground truth (Opus): the richest telemetry is ALREADY captured and
  discarded (cluster/GPU DVFS residency, idle ratios, requested-vs-
  achieved P-states); the observed idle-baseline contamination is
  mechanically visible in `gpu.idle_ratio`; per-item windows need only a
  ~20-line generalization of the existing phase-window machinery.
- Resolutions (Codex concurred on all): adopt the ladder as ONE
  quarantined scored profile (P2-010), never a universal per-run tax;
  land rich-telemetry parsing + environment snapshots (P2-009) FIRST
  (zero capture cost, improves every bundle); neither displaces
  2M / P2-008 / Phase 3 / D-014.
- Process refinement (user direction): the "devil's advocate" role is
  reframed as a thesis-committee EXAMINER (test whether claims survive a
  hostile expert; obligated to name the version that passes), and plan
  syntheses get a FINAL fresh-context Fable examiner before being
  presented as settled. Recorded in the global council skill.


# C-005: Steelmanned research agenda + workload expansion (ideation/strategy council)

- Date: 2026-07-07. Session shape B (ideation/strategy; read-only over the
  repo; deliverables drafted to scratchpad for lead review).
- Participants: Fable orchestrator (grounding, discussion round, synthesis)
  + 5 parallel read-only Codex gpt-5.5 lenses: STEELMAN-MAXIMALIST,
  RESEARCH-QUESTION GENERATOR, UNEXPECTED-APPLICATIONS, DEVIL'S-ADVOCATE
  (examiner protocol per C-004: every attack must name the version that
  passes), and WORKLOAD/QUERY-SET DESIGNER (added mid-session at user
  direction). Each lens received the same orchestrator-prepared capability
  inventory (what the harness measures today, what is queued, hardware
  tiers, known limits) plus a distinct charge.
- Charge (from Ed): steelman how much more can be done with the benchmark;
  turn it into serious research questions, tiered by hardware; plus
  (mid-session addition) workload/query-set expansion as a first-class
  topic with a concrete starter-suite recommendation.
- Deliverable: `council_C005_research_agenda.md` (scratchpad), formatted to
  slot into `docs/research_question_bank.md`. Final shape: 8-paragraph
  steelman preamble; 16 Tier-1 questions (12 general + 4 workload-suite,
  current M3 Max only), 10 Tier-2 (named gates: P1-006 3050/Orin, 3080 Ti
  borrow window, P1-003 wall meter, P1-004 links), 5 Tier-3 acquisition
  classes with cost tiers; the `jw_mixed_v1` starter workload suite
  (6 categories × 8 items, n=5, fixed-budget greedy, 240 bundles ≈ 3-8 h
  per target/model/quant); 8 ranked applications + explicit
  deferred/killed application list.

## Unique contributions per lens

- **Steelman**: the auditability reframe (see adjudication 1 below — the
  lens attacked its own brief); "the big model costs time, not watts" as
  the unified-memory story; the fixed-vs-marginal model (Q4) as the bridge
  from benchmark numbers to app-level battery budgeting; "infrastructure
  outlives the result" as the strongest long-term claim.
- **RQ generator**: 20 questions with per-question trap-defused notes; the
  strongest new shapes were the time-vs-watts decomposition of
  quantization benefit (RQ-T2.1), joules-per-ACCEPTED-token for
  speculative decoding, runtime-attribution ("how much energy is the
  runtime's, not the model's"), and the keep-warm-vs-reload breakeven.
- **Applications**: the ranked-by-lowest-extra-work discipline; the
  prompt/template energy profiler and "attach-a-bundle" power-bug repro
  case as the two highest-leverage near-zero-work applications (neither
  had appeared in any prior council); the internal-tool-first ladder for
  every public-facing application.
- **Devil's advocate**: the detection-floor-vs-effect-size audit (which
  proposed questions are underpowered at n=5); the directional (not
  additive) bias of the Mac SoC boundary for memory-heavy workloads; the
  "checks the code can't cash today" list separating measured / queued /
  planned; the minimal defensible experiment design for the MoE scaling
  observation.
- **Workload designer**: the category-energy mechanism table
  (prefill/decode ratio, thinking-token inflation, output-length variance,
  tokenizer fertility); the synthetic-shape-control PAIRED WITH
  realistic-exemplar hybrid discipline; the `jw_mixed_v1` starter suite
  proposal; the "token counts explain everything" null result named as
  itself reportable.

## Adjudications (steelman position → attack → reasoning → outcome)

Recorded in full because the WHY must survive for future sessions; the
examiner named a passing version for every attack, so nothing was dropped
without a surviving scoped form. No follow-up Codex round was needed —
the disputes resolved by adopting the examiner's own named rewrites, and
the lead (orchestrator) found no case where a steelman claim and the
examiner's rewrite were actually incompatible.

1. **"Nobody publishes joules/token for local inference" — KILLED by the
   steelman lens itself, replaced by the auditability claim.** Steelman
   brief asserted the missing-public-data angle; the steelman lens
   fact-checked its own charge and found MLPerf Power, TokenPowerBench,
   and ML.ENERGY-style datacenter benchmarks exist. Reasoning: an
   importance case built on a falsifiable "nobody does X" collapses on
   first review; the true differentiator is that JouleWise numbers are
   auditable FROM RAW EVIDENCE (bundle + strict re-reduction), which no
   named competitor offers for local inference. Outcome: the preamble
   leads with auditability, not novelty-of-topic. Dissent: none.

2. **MoE active-params scaling (6.7× → 6.7× mJ/token, flat power) —
   SCOPED from "finding" to "hypothesis + designed experiment".**
   Steelman position: the 122B result is the flagship story of the
   unified-memory measurement window. Attack (examiner #8): one model
   pair, one quant, one runtime, one SoC, and the two models differ in
   family, reasoning-mode, and total params simultaneously — "scaling
   law" language is unearned; total-vs-active params, KV size, and
   runtime version are all uncontrolled confounds. Reasoning that
   decided it: the observation is real and striking, but its epistemic
   status is one data point on a line with two points; the honest form
   is the EXPERIMENT that would make it a claim. Outcome: killed the
   scaling-law WORDING; promoted the minimal defensible design to Tier-1
   RQ-T1.1 (4-6 model points, dense + MoE controls, same quant recipe and
   pinned runtime, fixed shapes, n≥5, interleaved, fitted with
   uncertainty; claim template "evidence for active-parameter scaling on
   MLX/M3 Max", never "MoE models scale with active params"). Dissent:
   none — steelman's own text had already hedged ("simple, falsifiable
   pattern").

3. **Carbon labels — KILLED as a near-term application; the
   local-vs-cloud crossover QUESTION survives.** Steelman/apps position:
   energy labels and carbon accounting are a natural use. Attack
   (examiner #1, #7): powermetrics is vendor-MODELED rail telemetry at a
   boundary that excludes DRAM-at-wall/display/PSU; a carbon number
   derived from it is unauditable at exactly the step the whole harness
   exists to make auditable, and grid-intensity assumptions compound it.
   Reasoning: the kill is about the LABEL (a public absolute claim);
   the underlying question (when is local inference energy-cheaper than
   a datacenter round trip) survives because it can be honestly framed
   as boundary-explicit, wall-meter-calibrated, and
   assumption-documented — the harness supplies the local side with real
   error bars, which is the currently-missing half. Outcome: carbon
   labels moved to "requires wall meter + stated grid assumptions,
   phrase as 'measured local inference energy on named boundary'";
   crossover economics kept as Tier-2 (wall meter gate). Dissent: none.

4. **Cross-device leaderboard / public model cards — SCOPED to an
   internal→public ladder.** Apps position: joules/token next to quality
   scores, public leaderboard on identical hardware. Attack (examiner
   #7, #3): one lab, one machine, no cross-lab reproduction, and
   boundary-inconsistent columns (SoC rails vs GPU board) would make a
   public table exactly the kind of unauditable artifact the project
   critiques. Reasoning: the defect is prematurity, not concept —
   pinned-condition internal tables are defensible today, and the
   path to public credibility is locked methodology + reference
   workloads + a second lab reproducing. Outcome: kept, with the ladder
   (internal tool → published methodology → cross-lab table) written
   into the application entry. Dissent: none.

5. **CI energy-regression gates — SCOPED with preconditions.** Attack
   (examiner #2, #7): run-to-run CV 0.3-1.4% today but across reboots /
   OS updates / charger states the variance envelope is unknown; a gate
   thresholded below the detection floor generates noise-failures and
   discredits the tool. Reasoning: the application is sound and is the
   natural consumer of the methodology-centerpiece detection-floor work
   already in the bank; the gate must be defined in units of the
   MEASURED floor. Outcome: kept as a top-3 application with
   preconditions (pinned host, environment snapshots from P2-009,
   baseline-refresh policy, threshold ≥ measured detection floor).
   Dissent: none.

6. **Iso-quality architecture comparisons — SCOPED into the C-004
   quarantine.** RQ-generator position: dense-vs-MoE at iso-quality is a
   publishable frontier. Attack (examiner #6): "iso-quality" smuggles
   back the killed intelligence-per-joule problem the moment quality is
   a free-form eval score; scorer choice, stopping policy, and
   answer-length distributions become unacknowledged experimental
   variables. Reasoning: C-003/C-004 already adjudicated this lane —
   the surviving form is the controlled-envelope ladder
   (affine_mod_ladder_v1) where difficulty is designed to hold token
   budget constant and correctness is an annotation. Outcome: RQ kept
   but rewritten to require either the quarantined ladder or
   benchmark-band MATCHING (pairing models others have scored, without
   JouleWise running the eval), and the claim template fixed to "energy
   per correct answer on this controlled ladder". Dissent: none — this
   re-affirms a standing kill rather than re-litigating it.

7. **Per-token / fine-timing claims — KILLED (re-affirmed).** Several
   candidate shapes (KV decode drift per token, sub-100 ms phase
   attribution, short-prompt prefill energy) run into the ~9 Hz sampler
   vs ~4 ms token cadence. Reasoning: standing C-003 rule; the examiner
   extended it to phase windows generally — any window with fewer than
   several samples reports "unidentifiable", not joules (this is
   exactly the queued identifiability-flags feature). Outcome: all such
   questions carry a CHUNKED-window methodology note; the 0.03 J
   prefill number is reported as "unresolved at this resolution", not
   as a measurement. Dissent: none.

8. **Small-effect questions at n=5 — SCOPED with a power precondition.**
   Attack (examiner #2): sampling-strategy overhead, small runtime
   deltas, and minor DVFS effects are plausibly below the ~1% CI width
   n=5 buys at the observed CV. Reasoning: rather than dropping the
   questions, order them behind the detection-floor measurement and
   prescribe the rescue design (paired ABBA/interleaved runs, n=10-20
   for ~1% effects — cheap on this instrument at 30-75 bundles/hour).
   Outcome: affected Tier-1 questions carry an explicit "requires
   detection floor first; n≥10 paired" note. Dissent: none.

9. **Single-machine generalizability — SCOPED by claim-type taxonomy.**
   Attack (examiner #3): every result is "one M3 Max in one apartment".
   Reasoning: the defensible survivors are (a) instrument claims, (b)
   within-target structure (ratios, decompositions, rankings on one
   box), and (c) existence proofs (ANE dark; contamination detectable);
   population claims need a second unit or second lab — which is what
   Tier 3 acquisitions are FOR. Outcome: the agenda's claim templates
   use "on this M3 Max / MLX / powermetrics" wording throughout, and
   Tier 3 names "a second M-series unit" as the cheapest
   generalizability purchase. Dissent: none.

10. **"The harness already supports X" wording — KILLED where X is
    queued.** Attack (examiner #9): uncertainty aggregation (D-014) is a
    dead field until P2-011; rich telemetry (P2-009), scored suite
    (P2-010), 2M matrix, remote targets, wall meter, and split runs are
    queued or planned, not landed. Reasoning: the steelman is a case for
    the INSTRUMENT + ROADMAP and must not misstate the present tense —
    exactly the drift the docs-consistency protocol exists to prevent.
    Outcome: the agenda's preamble and every RQ hardware line separate
    measured-today / queued / gated. Dissent: none.

11. **Boundary exclusions as DIRECTIONAL bias — ADOPTED as a
    methodology note on multiple RQs.** The examiner's sharpest novel
    point: the Mac SoC boundary doesn't just offset absolute numbers,
    it can BIAS COMPARISONS whose conditions differ in unified-memory
    traffic (long-context, KV-heavy, memory-bound workloads
    underrepresented relative to wall). Reasoning: this elevates Q6
    (boundary sensitivity) from calibration chore to a gating
    dependency for several Tier-1/Tier-2 comparisons. Outcome:
    KV-economics and long-context RQs carry "boundary-directional-bias"
    threat notes; the wall meter's value statement in the agenda cites
    this, strengthening the case for closing P1-003. Dissent: none.

12. **Workload categories vs "token counts explain everything" — BOTH
    outcomes pre-registered.** Workload-designer position: category
    (chat/code/summarization/reasoning/extraction/multilingual) is a
    real energy axis via prefill:decode ratio, output-length
    distributions, and thinking-token inflation. Orchestrator applied
    the examiner's frame: at fixed token shape, category differences
    may collapse to nothing the instrument can resolve. Reasoning: the
    suite is designed so EITHER result is publishable — shape-matched
    synthetic controls paired with category exemplars make "energy/token
    is shape-determined, category-invariant" a strong reportable null,
    while thinking-token inflation (measured on the already-benchmarked
    reasoning flagship) is the category effect most likely to be large.
    Outcome: `jw_mixed_v1` adopted as the recommended starter suite
    with paired controls and greedy decoding + recorded stop reasons
    (EOS-bias audit inherited from C-004). Dissent: none.

## What the devil's advocate killed outright (summary list)

- Unqualified absolute-joule claims from modeled rails.
- Carbon LABELS (the application, near-term; the crossover question survives).
- "Scaling law" language from the 2-model MoE observation.
- Per-token energy claims and short-window phase joules (re-affirmed).
- Public cross-device leaderboards before wall calibration + cross-lab
  reproduction.
- Sub-detection-floor CI gate thresholds.
- Present-tense capability wording for queued features.
- (Re-affirmed standing kill) general intelligence-per-joule.

## Dissents

None outstanding. The lead notes one deliberate tension left in the
agenda rather than resolved: the steelman ranks the split-inference study
(Q1-Q3) among the top-3 claims while the examiner's hardware audit makes
it the most gate-dependent item in the entire agenda (links + second
node + borrow window). The agenda records both positions; the existing
feasibility-first Phase 3 ladder is already the mitigation.

## Process notes

- One operational failure: the fifth (workload) Codex lens initially
  hung on stdin when launched in background (`codex exec` read stdin);
  relaunched with `< /dev/null`. Worth folding into the codex-delegation
  skill's invocation notes.
- The examiner-names-a-passing-version protocol (C-004 refinement)
  measurably paid off: it converted what would have been 8+ discussion
  rounds into direct adoption of pre-negotiated rewrites; zero follow-up
  Codex rounds were spent.
- Spend: 5 Codex lens invocations + orchestrator grounding/synthesis;
  no repo mutations (session shape B honored).



## C-006 (session trace + meta-review, 2026-07-07): six-stream parallel batch, integration review, process meta-review

Streams: A uncertainty/D-014 (in flight) · B campaign automation (merged,
PR #3) · C mock-hardening/P2-008 (in flight) · D rich-telemetry/P2-009
(merged, PR #4) · E kv-size helper (merged, PR #2) · F repo test-audit
(in flight). Plus: ideation council (DL-1) and a post-merge Codex
integration review over merged main.

### Shape (orchestration decisions)

- **Decomposition — 5 implementation streams + 1 audit stream, parallel:**
  the queue held independent, file-disjoint tasks; worktree-per-stream
  isolation makes collision structurally impossible (checked against
  expected `git diff --stat` footprints before fan-out). Sequential would
  have serialized ~15-min Codex rounds behind each other for no safety gain.
- **Model assignment:** Fable for stream orchestrators — each stream needs a
  judgment GATE (final-diff review, finding triage, commit decision), not
  volume analysis. Codex 5.5-high for all implementation/review/test volume —
  near-limitless quota makes redundant fresh-eyes passes free, and fresh
  Codex instances carry no thread state, so a fresh instance is a genuinely
  independent reviewer even of Codex's own code. (Gen-1 launch violated
  this by accident — see I-2.)
- **Review tier per stream (scaled by cost-of-being-wrong):**
  - A, C, D — measurement semantics; a defect poisons the scientific
    validity of every future number → FULL: Codex design round, 3-lens
    counterreview, test amplification, writer≠reviewer test review, lead
    live-verify.
  - B — operator-facing campaign script; failure wastes a session, not the
    dataset → standard: counterreview + amplification + fresh test review +
    orchestrator live-verify against the real CLI (which is what caught K-4).
  - E — pure calculator, no runtime surface → lighter: counterreview lenses
    + orchestrator diff gate (which caught K-1..K-3 — the light tier still
    carried its weight).
  - F — audit-only; findings reported, never fixed in-stream (other streams
    own the code).
- **Ideation council: 4 lenses + devil's advocate** — breadth beats depth
  for agenda-setting; divergence is the point (council skill, shape B).
- **Post-merge integration review added** because per-stream review
  structurally cannot see cross-stream interactions. Vindicated same
  session: it found 2 real interaction defects (K-9, K-10).

### Catches (differential attribution)

| id | what | sev | caught by | missed by | enabler | counterfactual |
|---|---|---|---|---|---|---|
| K-1 | silent head_dim floor in KV-size calc | med | fresh-eyes Codex counterreview lens (E) | Codex implementer AND Fable orchestrator review | writer≠reviewer: fresh instance, no thread state | wrong KV payload numbers feed Phase-3 transfer planning |
| K-2 | text_config precedence ignored (nested config) | med | same lens (E) | same both | same | wrong KV numbers for exactly the model class we benchmark (MoE/nested) |
| K-3 | bare-ValueError catch-tuple, over-broad blast radius | should-fix | Fable orchestrator diff gate (E) | Codex implementer | Fable-final-gate doctrine (thin ≠ rubber stamp) | unrelated errors silently swallowed as parse failures |
| K-4 | campaign resume checks a path the real CLI never creates | blocker | orchestrator LIVE-verify vs real CLI (B) | implementer + its GREEN tests (the stub encoded the same wrong contract) | live-verify doctrine: tests green never sufficient | first real overnight campaign silently fails to resume |
| K-5 | campaign robustness ×5: lock, torn log, sanitization, half-written summary, config-error abort | should-fix ×5 | Codex counterreview lenses (B) | implementer | mandatory counterreview after every implementation | operator-facing failures mid-campaign, partial evidence on disk |
| K-6 | rich-write failure aborted stop_sampling AFTER raw preservation | blocker | Codex counterreview (D) | implementer | mandatory counterreview | a parser bug destroys the very run it instruments — violates D-002's re-reduce promise |
| K-7 | runtime-clock anchoring broke regenerability-from-raw | blocker-class | test-AMPLIFICATION round (D) | implementer AND counterreview | amplification WRITES adversarial tests, doesn't just read | bundles not re-derivable from raw/ — core auditability promise broken |
| K-8 | lead's own verification run contaminated (agent-fleet display compositing held GPU ~75% busy) | measurement-validity | the idle-quality gate ITSELF (D) — its first true positive | the LEAD's prediction | building quality gates into the instrument | contaminated idle baseline blessed into the corpus; instrument outperformed operator |
| K-9 | stale-config glob landmine across streams | should-fix | post-merge Codex integration review | every per-stream review (structurally blind to it) | integration-review step exists precisely for this class | first mixed-stream run trips on stale configs |
| K-10 | unconditional per-rep env capture (cross-stream interaction) | should-fix | same | same | same | per-rep overhead inside measured runs |

### Deliberations (design-bearing disagreements only)

- **DL-1 (ideation council):** recorded in full in the C-005 entry above
  (12 adjudications, each position -> attack -> reasoning -> outcome ->
  dissent; per-lens unique contributions; killed/deferred list). Pointer,
  not copy, per one-fact-one-home.
- **DL-2 (stream D, idle-gate shape):** counterreview lens attacked the
  implemented min-based suspect rule as too twitchy — fixture margin to
  false-positive was 0.047 on `gpu_idle_ratio_min`; a single scheduler blip
  would flag a clean idle window. Orchestrator position: min is the honest
  detector (one busy sample = contamination). Resolution after 1 round:
  persistence rule adopted (suspect iff >=40% of idle samples below 0.80
  GPU idle_ratio OR mean GPU freq > 800 MHz) — contamination that matters
  is sustained, blips are noise; boundary tests pin both sides. Lens
  prevailed; no dissent recorded. Binds: the 0.40 threshold has no
  empirical contaminated-window corpus behind it yet (revisit flagged in
  PR #4).
- **DL-2b (stream D, artifact placement):** Codex argued rich derived
  JSONL must NOT live under `raw/` — "derived data under raw/ weakens
  raw-as-source-of-truth (D-002)"; a top-level artifact via a
  `write_derived_artifact` seam needs zero controller plumbing and keeps
  D-024. Orchestrator accepted, added the idle-window variant Codex had
  not proposed. Both prevailed in part; outcome is the committed layout.
- **DL-2c (stream A):** design amendments (plain JSON aggregate dicts with
  UncertaintyInterval internal to n>=1 paths; structured problems instead
  of exceptions) — stream still in flight; its final report carries the
  full block per the standing trace requirement.
- Streams B/E: no qualifying deliberation blocks — findings accepted on
  argument without design-bearing dissent. Zero blocks is a valid outcome.
- Merged streams B/E: no qualifying deliberation blocks known to this
  reviewer — findings were accepted on argument without design-bearing
  dissent. Zero blocks is a valid outcome.

### Interventions (lead acted from outside the agents' self-reports)

| id | failure mode | detected via | fix | folded into |
|---|---|---|---|---|
| I-1 | 2/5 gen-1 orchestrators stalled, ending turns to "await" a poll-only bridge | lead observed ended turns with idle Codex processes | prompts now MANDATE poll-in-turn or background-Bash + watcher | codex-delegation + multi-stream skills, same session |
| I-2 | all 5 gen-1 streams silently inherited Opus (session accidentally started on Opus) | lead inspected spawn config, not agent self-reports | explicit `model: "fable"` mandatory; relaunch was CHEAP — worktree diffs, bridge state, and Codex `resume --last` all survive agent death | multi-stream skill |
| I-3 | one Codex lens wedged silently ~50 min (stdin hang: `codex exec` in background Bash without `< /dev/null`) | OUTSIDE evidence only: `ps` etimes + output-file mtimes vs finished siblings (agent reported nothing) | external kill; `< /dev/null` mandatory on every `codex exec`; fleet-health-check practice born (classify long-runners from ps/mtimes, never self-reports) | codex-delegation + multi-stream skills |
| I-4 | stream A accidentally stopped by the user | SendMessage returned "no active task" while siblings returned "queued" — a reusable stopped-stream detector | relaunch on surviving worktree state | this log (diagnostic recorded) |

### Layer yield + spend (rough; spend capture starts next session)

- Fresh-eyes Codex counterreview lenses: 2 unique (K-1, K-2) + 6 robustness
  (K-5, K-6). ~free (Codex quota).
- Fable orchestrator diff gates: 1 unique (K-3). Orchestrator context.
- Orchestrator live-verify vs real CLI: 1 unique blocker (K-4).
- Lead live-verify: 0 unique catches this session — but was itself CAUGHT
  by K-8; the layer's value this session was running the instrument that
  outperformed it.
- Test amplification: 1 unique real bug (K-7) + 14 edge tests (B).
- Fresh-instance test review: 6 vacuous/tautological tests fixed (B) + 2
  mutation gaps (D). No unique code bugs — on watch as a BUG-catch layer;
  clearly earning as a TEST-quality layer.
- Integration review: 2 unique (K-9, K-10) on its first outing.
- Opus refuter tier: not used this session; 0 unique catches for 2+
  sessions → drop from default roster per the council's own rule (C-006).

### Doctrine changes (adopted this session, each folded same-session)

1. Liberal Codex — near-limitless quota → counterreview after EVERY
   implementation is the default (council + codex-delegation).
2. Test doctrine: amplification round + writer≠reviewer fresh-instance test
   review (codex-delegation).
3. Apex/volume split: Codex = volume (reading, lenses, tests, computer
   use); Fable = orchestration + final gates (codex-delegation + council).
4. Failed-test triage: Codex first, Fable after 2 Codex failures
   (codex-delegation).
5. Poll-or-watcher mandatory in orchestrator prompts (I-1) (codex-delegation
   + multi-stream).
6. Explicit `model:` on every orchestrator spawn (I-2) (multi-stream).
7. Fleet health checks from outside evidence, on landing or ~hourly (I-3)
   (multi-stream).
8. Post-merge integration review is a standing step (K-9/K-10)
   (codex-delegation).

### Meta-review C-006 verdicts adopted (same session)

- Council log was HALF-INSTRUMENTED (catch attribution prose-only, zero
  spend records => drop-a-layer unenforceable). Fix: this entry is the
  first in trace format v2 (Shape / differential Catches / Deliberations /
  Interventions / Layer-yield); v2 + threshold adopted into the council
  skill. Spend capture starts next session.
- Opus refuter/verifier tier DROPPED from the default roster: zero unique
  catches since C-001; function absorbed by fresh-instance Codex
  counterreview + Fable gates. (The council's own evidence rule, applied
  to itself.)
- Skills stack violated one-fact-one-home (doctrine restated up to 4x,
  memory file a shadow copy; adversarial-review doctrinally stale,
  pre-apex/volume) — dedup + adversarial-review update ordered same
  session; consistency-sweep scope extended to the skills themselves.
- Raw .codex-bridge logs: distill + quote into traces; archive to the
  R-016 backup area on worktree removal; never commit; prune after the
  entry lands. (This session's logs archived before cleanup.)
- operation-loop skill (single conductor-score loop over all meta
  processes,every step with skip conditions) drafted; pending lead gate.

### C-006 addendum (post-entry landings, same session)

- **Streams A and C landed** (PRs #6, #5) after the entry above was written;
  all five implementation streams + both integration fixes are now merged.
  New catch rows: **K-11** (A, stats lens): OverflowError crash on huge JSON
  ints in aggregate math — real bug, fixed with structured
  `non_finite_overflow` status. **K-12** (A, same lens): non-finite
  `Infinity` leakage into manifest JSON from extreme spreads/subnormal MAD —
  fixed (nulled + status; outlier kept with `modified_z: null`). **K-13**
  (C, orchestrator): review-lens over-strong assertion (all samples strictly
  interior) cut to the reducer's actual contract — the one genuinely flaky
  assertion removed before it could poison CI.
- **Deliberation blocks now on record** in the stream reports (quoted in
  full there; key adjudications): A's load-bearing disagreement — Codex
  refuted populating per-member `SummaryMetrics.uncertainty` ("structurally
  wrong: one interval with one mean, while D-014 needs intervals for many
  metrics"); orchestrator accepted but required each aggregate entry to BE a
  serialized `UncertaintyInterval` — hybrid resolution, both prevailed in
  part. A's orchestrator also overrode 2 test-review BLOCKERs (downgraded
  with rationale; the lens's mutation concern adopted via a
  poisoned-aggregate test) and accepted Codex's stricter
  no-auto-without-outliers reading of D-014. C's three-way design
  adjudication: (a) unconditional interior stamping won because (b)
  clock-type detection "makes mock telemetry a different adapter under
  FakeClock than under SystemClock… would preserve the blind spot that let
  this composition bug escape."
- **Intervention tallies:** I-3 (lens wedge) recurred ×5 in stream C (incl.
  amplification + test-review rounds; orchestrator substituted a
  revert-mutation check: adapter reverted to HEAD → 13/18 new tests fail —
  the strongest writer≠reviewer evidence in the session) and once in C-005 —
  all before the `< /dev/null` fix propagated; zero recurrences after. I-4
  (accidental user stop) recurred ×2 (C-006 meta-agent mid-dedup; session
  restart killing A/F mid-flight) — both recovered loss-free from on-disk
  state (worktree + bridge outputs + scratchpad lens files), confirming the
  relaunch-is-cheap property as a designed-for invariant, not luck.
- **Integration findings closed:** INT-001 (stale-config refusal,
  `a05e54d`) and INT-002 (per-experiment shared env snapshot with provenance
  fields + deterministic FakeClock skip, `8856c04`), both Codex-implemented,
  lead-gated, live-verified.
- **D-014 acceptance evidence (lead, real hardware):** n=3 real MLX
  experiment → 10 metrics aggregated, energy/output-token 99.19 ± 1.36 mJ
  (Student-t 95%, CV 0.55%), `below_headline_protocol: true` correctly
  flagged, aggregate re-derived BYTE-IDENTICALLY from bundles alone.

---

## C-007: Whole-project design/planning council + P2-013 fix design (user-directed)

- Date: 2026-07-07. Participants: Fable (lead, final judge), Codex gpt-5.5
  (7 parallel read-only lenses + 1 round-2 attack session). Shape: ideation
  council (skill shape B) — lead wrote position briefs FIRST (9 P2-013
  positions, 7 project positions), lenses argued against them, lead
  adjudicated a synthesis, a fresh Codex session attacked the synthesis,
  lead ratified with the attack's changes. Two genuine rounds of
  cross-model back-and-forth; no implementation.
- Subject: Ed asked for a project-wide council — design, architecture,
  high-level docs, planning — with Fable as final judge.

### Resolutions (what the consensus settled)

P2-013 fix design (implementation stream to follow, Codex-led):

1. B2/S5 provenance check lands in DEFAULT validation
   (`BundleReader.problems()`), not `--strict` — structural-vs-analytic is
   the D-030 boundary and byte-provenance is structural. Metadata
   object-shape (B3) checks first. All 6 corpus bundles already carry the
   field (lead-verified).
2. B1 completeness: ONE shared summary validator used by both
   `_check_summary()` and `is_complete()`; required keys per status;
   succeeded ⇒ headline energy fields present AND finite; token-derived /
   idle-subtracted metrics stay nullable. D-011 amendment note.
3. Shared finite-number primitive in a new dependency-free
   `joulewise/validation.py` (unanimous); powermetrics RICH telemetry stays
   diagnostic-only, never gates a bundle.
4. B5 duplicate rail rows: reject via one shared trace-validation path
   consumed by both `summed_curve()` and default validation; covers
   single-rail manifests. D-027 amendment.
5. B8: temp-file + same-dir rename inside the low-level write helper;
   helper cleans only its own temps; adapters never own cleanup.
6. A1 leniency: last-frame-only, ≥1 complete frame required, dropped tail
   recorded DURABLY in bundle evidence (adapter diagnostic), midstream
   failures still fail. Truncation-vs-corruption is not provable without
   framing checksums; the durable diagnostic is the honest compensation.
7. **Raw-to-trace gate (the council's biggest new catch, examiner lens):**
   strict mode today proves summary ↔ `power_trace.csv` but never that the
   CSV derives from `raw/powermetrics.plist` — D-030's "re-reduces from raw
   artifacts" wording overclaims. Adopted: powermetrics-only strict
   sub-check re-deriving the trace from the raw plist (+ anchor offset),
   IN-STREAM with P2-013 before any 2M data; D-030 wording corrected.
8. Sequencing: P2-013 (now including the raw-to-trace gate) lands BEFORE
   the P2-006 campaign. Honest rationale recorded: the capture-touching
   subset (A1/A5, B8, rank 1, R2–R5, B1 resume semantics, B2 provenance)
   gates hardware time; the rest rides along because pins are written and
   bounded. Pre-named fallback P2-013a = that subset, if a rare quiet
   window appears first.
9. Commit grouping: planning lens's 7 invariant-shaped groups adopted OVER
   the lead's priority-shaped 7. expectedFailure pins flip in the same
   commit as each fix. Post-landing target: 415 tests / 0 expected
   failures + `--strict` green over all 6 real bundles without rewriting
   them.

Project level:

10. Critical path has flipped from code to data. Instrument FEATURE work
    stops after P2-013 until 2M data exists; carveouts: evidence-integrity
    fixes never stop; cheap contract-preserving amendments that protect
    future data interpretation are in scope pre-2M.
11. Pre-2M contract amendments (new task P2-014, trimmed by the attack
    round to true blockers): (a) summary provenance (reducer/schema
    version recorded in summaries) before the corpus exists;
    (b) `phase_energy_j` pinned GROSS-ONLY in v0.1 (idle-subtracted phase
    attribution is Phase 4 analysis policy) — decided in-council, needs a
    decision-log entry when implemented; (c) composite event node identity
    = `metadata` field (per the 2N.9 flag) as a DOC alignment note only;
    (d) design note pinning BundleReader = single-node bundles, future
    CompositeBundleReader = split bundles.
12. Architect verdict accepted: BundleReader / controller lifecycle /
    strict validation / runtime-adapter capabilities / event key-set all
    BREAK for Phase 3 composites — as designed, this is Stage 3.1 work,
    not now; item 11 is the cheap protection.
13. Machine-state queue lanes adopted: QUIET-MAC / AGENT-COMPATIBLE /
    ED-EXTERNAL; sessions pick the top task compatible with their lane.
14. Two-claim-track framing adopted: auditable local measurement (harness
    + Apple-Silicon characterization) is the guaranteed capstone; split
    inference remains the validating study that upgrades it — NOT demoted
    to optional. Q4 phrased as fixed-vs-marginal workload structure (not a
    scaling law — two confounded points); Q5 narrowed on one machine to
    workload/model/quant ranking stability.
15. Detection floor confirmed UNOWNED (echoes C-003's "methodology
    centerpiece") → becomes an implementation-backed Phase 4 acceptance
    gate tied to aggregation/claims: per-target/metric floor,
    minimum-sample rule for phase attribution (~9 Hz sampler cannot
    resolve 94 ms prefill standalone), effect-size-vs-floor table,
    below-floor claims read "not resolvable" never "no difference".
16. Docs: no new authority docs. Queued maintenance: PROJECT_STATUS
    update-ledger scheme (≤2 prose update blocks), README
    prototype-status banner + mock-path-first, three named drift fixes
    (AGENT_PLAN 2G/2H/2I checkboxes; Do-Not-Do-Yet desk-spike vs
    data-collection wording; playbook gate summary), slimmer M0 intake,
    RUN_STATE history trimming.
17. Execution order (next 5): P2-013 [AGENT] → P2-014 [AGENT] → P2-006 2M
    [QUIET-MAC] → Stage 3.0.1 spike [AGENT] → P2-010 → P2-012 [AGENT].
    Ed's parallel track [ED-EXTERNAL], explicitly flagged as a real
    coordination load: calendar, device access, borrow window, wall
    meter, P0-003 backup destination — ideally one pass.

### Deliberation trace (design-bearing disagreements)

- **Lead conceded PP6 (architecture) to the architect lens.** Lead's brief
  said "no new architecture work now"; architect showed five seams break
  for Phase 3 and named three cheap amendments whose cost explodes once
  the 2M corpus exists ("data outlives code"). Lead's counter — full
  composite work still waits — survived; the amendments did too. Both
  positions are in the consensus as item 11/12.
- **Lead's commit grouping lost to the planning lens.** Lead grouped by
  priority (blockers first); planning lens re-grouped by INVARIANT
  (finite-number policy as one cross-module commit) and showed the lead's
  group G was a grab-bag. Adopted wholesale.
- **The attack round caught the synthesis's own contradiction:** section B
  declared "evidence-integrity fixes never stop" while section A left the
  raw-to-trace gate's timing open — "those cannot both stand." Lead
  ratified in-stream placement. This is the second time (after C-002) the
  reverse/attack direction caught what all forward lenses missed.
- **Q4/Q5 promotion (PP3): strategist and project-examiner converged
  independently** on the same refinement from opposite starts — strategist
  from committee-risk economics, examiner from "would read as pre-emptive
  retreat unless framed as a floor." The convergent two-track wording was
  adopted verbatim-ish. Dissent recorded: strategist warned against any
  language making split sound optional; examiner conditioned the framing
  on 2M + detection floor landing first. Both conditions kept.
- **Overridden:** examiner lens (P2-013 round) wanted CLI/report/clock
  fixes deferred out of the stream as "polish in the defense queue"; lead
  kept them in-stream (pins already written, groups isolate risk, and the
  queue item's acceptance is "all 31 pins flip"). Recorded as dissent, not
  consensus.

### Per-layer catches (instrumentation)

| layer | unique catches | notes |
|---|---|---|
| design lens (P2-013) | shared-summary-validator + shared-trace-path designs; B1 "present ≠ non-null" trap; cleanup ownership | shaped 3 consensus items |
| examiner lens (P2-013) | **raw-to-trace gap** (biggest catch); durable-evidence condition on A1; historical-corpus non-rewriting policy | major-revision verdict drove real scope change |
| planning lens | invariant-shaped commit groups; run_bundle_layout/checklist/council-log bookkeeping omissions; 7-not-6 audit test files; RUN_STATE staleness | beat the lead's grouping |
| architect lens | five seams break for Phase 3; three pre-2M contract amendments; composite-reader split note | overturned lead's PP6 |
| strategist lens | machine-state lanes ratified; 3.0.1-before-workload-buildout; "feature work stops" carveout; Ed one-pass external push | |
| project-examiner lens | detection floor confirmed unowned + concrete gate spec; phase-attribution-below-resolution objection; two-point scaling confound | supplied the "one change" (item 15) |
| docs lens | update-ledger scheme; index drift (C-005/C-006 missing — fixed this entry); three named drift items; slimmer M0 | |
| attack round (Codex, fresh) | A/B contradiction in lead's synthesis; B2 scope trim; Ed-burden flag; D-030 wording overclaim; 6 code spot-checks all confirmed | ratify-with-changes; all changes accepted |

Spend: 8 Codex read-only sessions (~free per economics doctrine); lead
context spent on briefs, adjudication, and this record. Zero-unique-catch
layers: none — every lens landed at least one consensus-shaping catch.

### Follow-ups

- Queue: P2-013 re-ranked to 1 (scope grows by raw-to-trace gate +
  bookkeeping superset), P2-014 created, lanes annotated, Do-Not-Do-Yet
  wording fix — this session.
- Decision-log entries land WITH the P2-013/P2-014 implementation (D-011,
  D-027, D-030 amendments; phase_energy_j; provenance; lanes convention).
- Docs maintenance queued as its own task (item 16), not done inline.
- PROJECT_STATUS refresh + two-track framing: with the docs task.


---

## C-008: Multi-stream session, checkpointed (2026-07-07 PM)

Session entry (format v2), kept slim because the full Shape / Catches /
Deliberations / Interventions / Spend record was preserved VERBATIM as
`docs/run_reports/2026-07-07-checkpoint-session-trace.md`, and the
product state + restart instructions live in
`docs/run_reports/2026-07-07-checkpoint-multistream-session.md`. Do not
restate; read those.

Pointer entry (per the C-009 recording rule): all product state,
process learnings, per-layer catches, and the calibration aggregate
live in the run report + its Process Trace Appendix. One
deliberation-class fact belongs here: the session's process conventions
(ledgers v2, calibration schema, decision-review doctrine) were shaped
by a Codex review that OVERTURNED two lead-designed schemas — dissents
and adjudications in the trace appendix.


---

## C-009: Meta-review of the orchestration system (SIGNED consensus)

- Date: 2026-07-07. Participants: Fable (lead), Codex gpt-5.5 (2 blind
  analysis sessions + 1 conferral session). Shape: both sides analyzed
  the process architecture and all logs BLIND to each other, then one
  conferral round; Codex SIGNED with 2 amendments + 1 gap rule, all
  accepted. This entry earns full-entry status under its own rule
  (durable doctrine + a real position reversal).
- Blind convergence (both sides independently): hybrid topology by
  stream shape; foreground bounded waits for retained orchestrators;
  heartbeat = backstop not scheduler; Codex up-stack; ledgers keep with
  ride-code-commits discipline; docs consolidation to single-writer;
  preflight gates from the session's actual failures.
- Genuine disagreement + resolution: WHERE the durable session process
  record lives. Codex's architecture lens said council log; Fable + 
  Codex's own docs-audit lens said run report (trace as appendix,
  council log reserved for deliberation). In conferral Codex CONCEDED:
  "my earlier council-log-as-process-history position was too broad
  given the duplication evidence." Adopted: run report = the session
  record; council log = index rows + genuine-deliberation entries only.
- Codex amendments (accepted): bounded waits get a STALLED-handback rule
  (never infinite loops); retired ledgers leave a branch/hash pointer.
  Gap rule (Codex): every retired working artifact leaves a discoverable
  pointer in its replacement home — path, branch, hash, promoted vs
  intentionally not promoted.
- Evidence highlights that drove the consensus: the same checkpoint fact
  written into SIX surfaces (docs audit, cited per-file); the wake gap's
  two fleet-wide stalls; the calibration ledger's design-freedom signal;
  the docs audit falsifying a claim in the lead's own run report
  (missing D-CHECKPOINT).
- USER RATIFICATION CONDITION (Ed, same day, binding): Fable is the
  APEX and final say on all high-level processes — the smartest model
  on the team; every other model's role exists to save Fable tokens,
  never because its judgment is preferred; "lead" in all topology
  tables means the Fable main loop; adjudication of any challenge to a
  Fable decision is itself Fable's. Encoded in operation-loop §3 +
  multi-stream topology preamble.
- Consensus text: run report §"Meta-review consensus"; durable homes =
  the operation-loop + multi-stream-worktrees + codex-delegation skills
  (rewritten same-session). Migration executed same-session: trace
  merged into run report, RUN_STATE slimmed to pointer shape, queue
  cells slimmed, C-008 converted to pointer style, codex-run patch task
  queued.

---

## C-010: Resume + merge session — C-009 topology first full run (2026-07-07/08)

Pointer entry: all product state, the per-layer catch/yield table, the
delegation-calibration aggregate, and restart instructions live in
`docs/run_reports/2026-07-07-resume-merge-session.md` (Process Trace
Appendix included). PRs #8/#9/#10 merged (Ed-directed, after a
3-reviewer pre-merge oversight pass with lead triage + 5.5 fixes);
PR #11 open. Deliberation-class facts for this log: (1) the lead-driven
codex-run topology ran a full session with ZERO wake stalls and zero
heartbeats — the C-009 T1 hybrid is validated on its pipeline half;
(2) two PINNED wire contracts (B-14 ssh argv, B-15 remote-root
derivation) were overturned by the lens round after unit tests had
faithfully pinned the broken shapes — fixture-first streams now always
carry the full lens tier (folded into multi-stream-worktrees);
(3) a volunteered 5.5 addition (vLLM provenance) was rejected at the
lead diff gate for hashing fabricated token IDs as realized evidence —
first clear model-defect row in the calibration ledger; the correction
(node-realized IDs via /tokenize or structured absence) is ledgered
B-44 with D-033 pressure intact; (4) K5's audit pin was adjudicated
unsatisfiable-as-authored and corrected at equal assertion strength —
the pin-correction protocol (STOP-and-report → lead ruling → sanctioned
edit) worked as designed.

Addendum (same session): PR #11 subsequently MERGED under Ed's new
standing self-merge-with-review authorization; the final fresh-eyes
pass over its post-review commit caught a real crash path + broken
checklist snippets first (fixed as B-45/B-46) — validating the
final-head rule now in operation-loop §5. All four streams landed;
main suite 546 OK.

---

## C-011: Counter-review of the independent project critique (2026-07-08)

FULL ENTRY (genuine deliberation). An independent 5.5 critique of the
entire project (docs/project_critique_review.html — goals, docs,
architecture, tests, methodology, stack; "strong instrument, not yet a
settled study") was counter-reviewed per Ed's directive: four
verification lenses checked every claim against code/docs/decision-log
ground truth with citations; the lead drafted dispositions; a bounded
5.5-high discussion round adjudicated six contested points; consensus
was reached on all six (no recorded dissent). Separately and first, a
consensus round on the new docs/site pages reached full agreement
(11 review findings + 3 new from the discussion itself, all applied).

Verification verdicts (details in the four lens out-files, summarized
in the run-report addendum): the campaign fail-closed cluster CONFIRMED
unanimously (skip-if-summary-exists, ok==exit-0, failed members
skippable — the highest-leverage finding, directly in the 2M path,
sharpened by the lenses with the reducer's config-token-denominator
fallback); the methodology cluster CONFIRMED at implementation level
while partly settled at planning level (C-007/DOC-007/D-014/D-018
already own the policies; mechanics were missing); the architecture
cluster judged directionally right but mis-timed (all queued post-2M;
RemoteNodeSession rejected per B-1's revisit clause, run-ID
randomization rejected per D-010/D-022); the docs cluster partly stale
(main pages already reconciled) but caught the flagship report's
surviving active-parameter overclaim and two stale-open Mac risks.

Contested-point outcomes: (C1) historical records stay immutable — the
flagship overclaim is superseded by a dated ADDENDUM, not amended;
(C2) the PROJECT_STATUS process section stays per Ed's explicit
showcase instruction but drops its self-congratulatory register (the
critique's compression recommendation was DECLINED in part — recorded
here as the one place the council knowingly deviated from the critique,
on the owner's standing instruction; residual tension flagged to Ed);
(C3) the claims ladder is adopted NOW as a binding contract
(docs/contracts/claims_ladder.md, D-037) because it disciplines the
imminent 2M report, with per-claim IDs deferred to Phase 4; (C4) idle
fail-closed enforcement lives at the CAMPAIGN layer with manifest-level
waivers — D-011 run semantics and strict's evidence-integrity scope are
both preserved, and waivers are never written into bundles; (C5) phase
identifiability ships pre-2M as a sample-count rule (>=3 per nonzero
interval) with the energy-floor gates arriving via the new P2-015
calibration campaign; (C6) 2M ordering is model-blocked,
workload-rotated, counterbalanced with a recorded imbalance — full
round-robin rejected for reload cost per D-014's own carve-out.

Implemented same-session on stream/critique-response (ed31d84, dbc37ed,
a42aeed): fail-closed campaign runner + verdict block + waiver schema,
counterbalanced order manifests, reducer honesty flags, claims ladder +
D-037, flagship addendum, stale-docs batch, R-002/R-003 re-scope,
P2-015/P2-016 queue items. Suite 546→555; 6/6 legacy bundles remain
strict-valid; mock e2e strict-valid.

Process note for the meta-loop: the deliberation rounds themselves had
independent yield beyond adjudication — the site round contributed three
findings its own source review missed; the critique round tightened two
designs into mechanical rules (C5's sample threshold, C6's rotation
scheme). Discussion-before-decision is earning its cost.

Addendum (2026-07-08): a second-pass reassessment was added to
`docs/project_critique_review.html` after C-011 implementation. Lead
fact-check verified 16/17 checkable claims; the one stale claim was the
Mac powermetrics/MLX risk-register wording, now annotated because
R-002/R-003 are closed-residual. The second pass updated several
first-pass passages in place and marks them in-document; the verbatim
C-011 first-pass text remains in git history at commit 6418084. A
follow-up fix pass added provenance layering annotations, hardened the
reassessment against repo evidence, and recorded this addendum-only
process footprint; the process-doc entries themselves are addendum-only.

## C-014: Workload-suite science hardening council (2026-07-08)

FULL ENTRY (genuine deliberation; position reversals recorded). Convened
on Ed's session directive: harden the science the prompt/workload suite
can answer and decide what to build next. Shape: lead independent audit
(formed before any lens output, deliberately), Codex scout packet, three
fresh Codex design lenses (statistical power/DoE, negative-space
consumer audit, adversarial confound hunt), lead triage with
dispositions, one Codex peer counterreview of the full synthesis with
design judgment explicitly invited, lead adjudication. Design docs
implemented by a pinned Codex session; lead diff gate before commit.

Convergent blockers (lead + all three lenses independently): Q4
unreachable at L3 from the 2M 4-cell grid; P2-015's absolute floor is
not the comparative MDE that gates L2/L3 claims. Unique catches by
layer: skeptic — jw_mixed category x shape confound (the C-W.1 null was
unfalsifiable as designed), silent long_short cap divergence, drift
sentinels, content-sensitivity sentinel promotion; power — the MDE
arithmetic (n=5 resolves ~1.5-1.8x CV), C5-1.1 between-model df
insufficiency, rank-gap rule, binomial energy/correct guard;
consumers — Q4-Q6 had NO Phase 4 figure/claims-index consumers, P2-010
substrate/ladder split, energy_token_j over-promotion under config
denominators; scout — phase-gross vs idle-subtracted headline mixing,
token_count_source naming drift, summary_provenance not strict-required.

Deliberated outcomes (all consensus; no dissent recorded):
(1) P2-010 splits into substrate + smoke ladder, full scored campaign
deferred — amends C-004's packaging; peer AGREE. (2) jw_mixed_v1 runs
phased with a common-shape identification stratum — supersedes C-005's
fixed-budget-full-first sequencing; peer AGREE ("spend-before-
identification"). (3) Quiet-window packing: lead leaned one window; peer
OVERTURNED to two (MDE-sized n cannot precede the floor campaign; a 4-6h
single window raises drift risk exactly while establishing a floor) —
lead adopted. POSITION REVERSAL. (4) Q4 grid: lead proposed 3x3; peer
AMENDED to 4x3 with named interpolation + extrapolation holdouts and
categorical-additive-first fitting — lead adopted. POSITION REVERSAL.
(5) analysis-plans contract adopted as a compact binding table (D-038);
peer contributed the full field schema and the pseudo-replication rule
(item windows are not independent replicates) — a gap every other layer
missed. (6) Consumer-lens implication that the next suite must include
the split matrix REJECTED: Q1-Q3 are Phase 3's by design (D-034 gate
unchanged).

Bindings: D-038 (analysis plans), D-039 (workload program v2). Queue:
P2-015/P2-006/P2-010/P2-012 amended; P2-019/P2-020/P2-021 added.

Meta-loop yield note: the invited-peer-design pattern paid again — two
lead designs overturned with strictly better ones (grid, window
packing), consistent with the 2026-07-07 calibration signal that
design-freedom delegation to 5.5 runs hotter than doctrine assumed.
Every layer produced unique catches this session; no drop candidates.

## C-015: Benchmark expansion council — suite architecture v2 + interop (2026-07-08)

FULL ENTRY (genuine deliberation; same-day second convening after
C-014). Convened on Ed's directives: (1) an extensive review of what
scientific questions the benchmark can answer and what measurements are
being left on the table; (2) expansion toward multi-prompt suite runs of
varying difficulty/type and benchmark interop in both directions;
worktrees + liberal Codex agents authorized. Shape: two reach lenses
(R1 affirmative capability map; R2 missing measurements), two design
lenses (E1 suite architecture/statistics; E2 interop), lead synthesis,
peer counterreview with design judgment invited, lead adjudication.

Reach outcomes: R1 mapped every answerable question by claim ceiling
(today / Window A / Window B / hardware-gated) with ladder-compliant
claim templates — landed as the bank's capability-map section; its
verdict named three unscheduled cheap campaigns (C5-1.6/1.12/1.8),
queued as ONE select-after-floors row (P2-024). R2's
collect-now-or-lose-comparability set (per-bundle env snapshots,
cooldown-trace preservation, inter-run gaps, tokenize/setup phase
markers, MLX memory snapshots, sampler-availability metadata) spawned
the window-a-capture worktree stream the same hour — the class of
finding that had to precede the 2M corpus' birth.

Design outcomes (consensus; peer narrowed, did not overturn): suite
architecture v2 (D-040 — B x k with r_within=1, bundle-level n,
one-mechanism architectural line, k=24, difficulty as quarantined
metadata); interop direction (D-041 — thin import manifests, HumanEval
smoke first, marker-shim energy layer with a verdict-shaped spike,
export prioritized for adoption-per-build-day, kill list). Peer's
unique catch: PER-ITEM FAILURE ECONOMICS — without a per-item
validity/status model + aggregation rules, suite breadth creates
ambiguous partial evidence; adopted into the P2-010a substrate
definition. Peer also drew the capstone stop-line (guaranteed capstone
= instrument + Mac characterization; expansion drops first under
pressure) and restated the D-034 gate — both landed in the 2O plan.

Layer yield note: all four lenses + peer produced unique catches;
the invited-peer pattern again narrowed designs materially (minimal-
substrate cap, energy-layer-only pin, gate amendment). Zero dissent
recorded; the round's three open design questions (substrate scope,
import-vs-export priority, capability-map home) resolved in one
counterreview pass without a second discussion round. A post-landing
verification workflow (3 lenses + refuters) then caught one blocker
(the 2O section retaining the superseded C-014 substrate enumeration)
and six should-fixes (level-marker omission vs AP-5, D-039-allowlist
drift worded as restatement, lossy D-041 kill-list record, an inflated
HumanEval floor claim, unlanded R2 dispositions, P2-010 gate omission)
— all fixed pre-commit; the verification layer earned its keep on its
first C-015 outing.

AMENDED 2026-07-08 (suite-build adjudication, D-044..D-047): the C-015
minimal-sketch is amended in three adjudicated ways — per-item response
TEXT ratified into `outputs/suite_items.jsonl` (D-045.8), the
`markers:`/`outputs:` blocks pinned as optional-defaulted-validated
constants inside the hashed effective manifest (D-044/D-045.3), and an
additive per-item `prompt_token_ids` source added for ids-native
sentinels (D-045.5/D-046). Dispositions for all 37 research-report
amendments: suite_implementation_research.md §Adjudication.

## C-017: Suite-build adjudication + implementation gates (2026-07-08)

Shape: Codex disposition draft over the 37 unresolved research-doc
amendments (invited design judgment, 8 argued lead calls) → lead
decisions → fresh Codex adversarial round on the decision batch →
implementation in 3 streams (substrate 3 units; affine; generators) each
with 2-3 fresh lenses + fix rounds → 1 Opus fresh-eyes substitute during
a Codex quota outage → 7-reviewer pre-merge oversight → 3 final-head
passes → post-merge integration review. Full narrative + per-layer catch
rows: `docs/run_reports/2026-07-08-suite-build.md` (process trace
appendix).

Genuine deliberations (positions moved): A3 manifest identity — lead
proposed raw-file-bytes hash, counterreview AMENDED to the canonical
EFFECTIVE-manifest hash (defaults inside identity; accepted, D-044); B5
BOS parity — lead DEVIATED from the draft's BOS-normalize
recommendation to ids-native-all-five (control must remain the incumbent
stream byte-for-byte); attack sustained with a binding
non-generalization caveat (D-046). Affine sentinel redesign: lens caught
that tag-forced duplication corrupted level denominators; lead chose the
dedicated-sentinel-item shape over relaxing SUB-1 (D-047.2 amendment,
k=25/26).

Layer yield (unique catches): lead live gates 3 (all
integration-reality class: cwd refs, strict rollup provenance, sampler
API namespace — invisible to 680+ unit tests and 9 lenses); oversight
10+ (incl. two validation holes: tamperable rollup digest,
vanishing group markers); unit lenses ~20; Opus substitute 1 major
(tokenize-window bracketing, FakeClock-blind); adversarial adjudication
round 4 (effective-hash identity gap the standout); integration 0
(clean). Process slip recorded: PR #18 merged into its stacked base
(retarget missed); recovered same session via promotion PR #20; lesson
folded into multi-stream-worktrees skill.

Addendum (2026-07-09, C-027 review, MET-001 / REV-4): the PR #18 merge
fdcf800 landed into suite-substrate, not main, and required promotion
PR #20 (84a70ca) to recover. Reclassified from operational "slip" to a
MERGE-GATE BREACH: D-031 requires PRs to land to main, and the merge
gate requires sibling merge-order simulation, which would have caught
the wrong base. Code outcome was fully recovered; the gate failure
stands as recorded. No history rewrite.

## C-018: D-013 alignment-capture window fix (2026-07-08)

Shape: background-chip session for the C-017 oversight spin-off
(alignment capture inside the measured window; predates the suite
substrate, since de5f04a). Solo lead implementation — a two-line
reorder in `_stage_measured_run` (stamp `sampling_stopped_s` as soon
as the runtime returns, then capture alignments) plus two regression
tests (`AlignmentCostTelemetry`: costly `clock_alignments()` must not
change metrics or move the stop marker) — with one light Codex
read-only review of the final diff (timing-semantics-adjacent, so the
cross-model pass ran despite the small size; no council per rule 3).

Layer yield: the catch itself is credited to the C-017 oversight
layer. This session: lead live verification proved both tests fail
pre-fix (gross_energy_j 0.84 -> 38.34 J under a 5 s simulated capture
cost) and re-ran the full suite (734 green); Codex review returned
approve with zero findings (it independently re-checked
`measured_window()` in bundle_read and the failure-path stop helper).
Landed: PR #21.


## C-019: Post-suite-build meta-reassessment (2026-07-08)

Standing §10 trigger (multi-PR session; Ed directed the full run after the
parallel alignment-fix session landed as PR #21). Shape: 4 parallel Codex
analyst lanes + completeness critic; lead synthesis. Lane outputs
preserved in the session scratchpad; conclusions and dispositions here
and in the run-report addendum.

Lane findings adopted:
- 5.5-DIRECTION STUDY (priority lane, 43 invocations deep-sampled):
  direction doctrine distilled and FOLDED into the codex-delegation
  skill — precedence sentence, autonomy clause, FIX-N fix contracts
  (7/7 one-shot), angle-named lenses, production-shaped gate
  requirement, checks-performed line for CLEAN verdicts, stack-context
  for reviewers; RELAX list (invariants not structure; shorter reads
  when facts embedded; early design-freedom). Post-upgrade expansion
  candidates recorded with safety gates; calibration labels declared
  MODEL-VERSION-SCOPED with a sealed-A/B re-baselining rule before any
  boundary move (critic item 1).
- CALIBRATION LONGITUDINAL: design-freedom-runs-hot confirmed across
  C-010/C-014-15/C-017 (high judgment yield, gates still mandatory); no
  active layer at two consecutive zero-catch sessions; WATCH items:
  integration-after-clean-oversight (one zero at C-017, C-010 contra),
  Opus-vs-Codex fresh-eyes A/B (sealed same-packet protocol defined; ≥2
  trials before roster change). Prompt-defect class active (~2/large
  session, lead-side); quality denominator (false-positive burden,
  severity mix, triage cost) noted as missing instrumentation (critic 7).
- PROJECT STATUS: the guaranteed capstone hinges on the 2M corpus; the
  critical path is P2-015 floors → P2-006 2M → baseline_results.md →
  Phase-4 claims scaffolding. P1-008 calendar mapping ELEVATED to
  ED-EXTERNAL rank 1 and extended with the evaluator acceptance-bar ask
  (critic 8). P2-025 re-ranked adjacent to the real-tokenizer manifest
  work. R-012 schedule risk named the biggest active management risk;
  R-016 interim backup becomes serious before 2M.
- CLOSURE: D-013 prose/docstrings back-annotated to marker-bounded
  wording (this batch); C-018 index row added with commit hashes;
  RUN_STATE 734; bank affine-queued line amended. Derivability clean.
- CRITIC dispositions: (1) sealed A/B re-baselining ADOPTED (skill);
  (2) pre-#21 bundle validity — alignment-capture overhead is
  dict-read-scale, corpus remains claim-usable, recorded here, no
  re-reduction; (3) quiet-window/upgrade-exploration conflict — upgrade
  experimentation is [AGENT]-lane, never in quiet windows (C-009 T5
  extends); (4) post-merge SHAKEDOWN GATE adopted into P2-015 row (one
  tiny production-shaped campaign-runner run before Window-A data);
  (5) skill folds listed with paths in the run-report addendum;
  (6) site regen rides this batch; (7) noted above; (8) adopted into
  P1-008.


## C-020: Stop-and-analyze whole project — technical + research merit debate (2026-07-08)

Event class: owner-directed whole-project merit review ("strictly
technical and research merit; logistics off-limits; split study is
happening"). Largest review event to date: a 69-agent Workflow (5 codex
readers over all top-level docs + code + evidence, 2 web freshness scans
[2026 energy-benchmark landscape; split-inference energy literature],
5 assessment lenses [technical feat / benchmark merit / audience /
research questions / skeptic], per-finding adversarial verification
tiered by materiality, synthesis + attack round), PLUS two independent
Fable position papers (session lead, written pre-workflow-output; fresh
Fable subagent with no session context), PLUS a recorded Fable-vs-Codex
debate round and lead adjudication. Artifact: the corrected assessment
is committed at docs/reviews/2026-07-08-technical-merit-review.md;
position papers and debate transcripts in the session scratchpad;
verdict summary in the run-report addendum.

CONVERGENCES (all three poles independently; no debate needed):
- The distinctive technical feat is the composed EVIDENCE ARCHITECTURE
  (auditable raw-to-claim chains, marker-bounded windows, strict
  re-derivation) plus the clinical-trial-style claim-gating stack
  (ladder/floors/pre-registration) — plausibly field-first for energy
  benchmarking; the components individually are well-executed-standard.
- Machinery is ahead of data: ~six real bundles gate hundreds of pages
  of methodology; nearly all research merit is promissory until the
  campaigns run. Correct failure mode for this stage, but graded as
  instrument + de-risked path, not results.
- Sensor trust (vendor telemetry, uncalibrated) is the binding validity
  ceiling; the wall/USB-C bridge is load-bearing methodology.
- Pre-registering a compositional split-energy prediction before split
  hardware runs (lead Thesis 5 = fresh-Fable "spine inversion" = Codex
  "elevates Q1 to transferable theory") → promoted as D-048.

DEBATE RULINGS (lead adjudication after Codex round 1; dissents kept):
- D1 question ranking: coupled Q4→Q1 (compositional prediction +
  first-of-kind per-stage dataset) #1; TOKEN-SHAPE SUFFICIENCY NULL
  SUSTAINED at #2 over fresh-Fable's omission (equivalence-margin
  results travel: a holding null validates every shape-matched synthetic
  energy workload; a failure confounds every shape-only benchmark); Q6
  boundary bias ELEVATED to #3 (fresh-Fable's "most citable by other
  benchmark authors" conceded by Codex); active-parameter scaling #4;
  affine ladder reclassified per D4; Q5 last ("unresolved ties" likely;
  the MDE discipline is the contribution, not the answer).
- D2 crossover prior: fresh-Fable CORRECT against the original Codex
  draft — debate arithmetic (Qwen2.5-1.5B: 28,672 B/token → 56 MiB @
  2048 tokens → ~0.5 s on 1GbE; 8B @ 8192 → ~9 s; second-device
  overhead 5-50 W → 2.5-25 J against tens-of-joules prefill savings)
  places crossover as possible-not-uniform: favored by asymmetric
  device strengths, long prompts, ≥2.5GbE, low-idle pairings. This
  arithmetic is why D-048 is mandatory, not stylistic.
- D3 spine: synthesis adopted — model-first FRAMING, dataset-first
  CONTRIBUTION (thesis sentence in D-048). Fresh-Fable's strong
  inversion declined: the both-end per-stage decomposition dataset is
  first-of-kind regardless of model fit.
- D4 affine ladder: lead position sustained — a suite-validity and
  denominator-discipline instrument, not a headline; C5-1.9
  (MoE-vs-dense energy-per-correct) exempt. Codex conceded its stack
  overstated the ladder's scientific independence.
- D5 cheap validity moves, priority: (1) publish a bundle pack + obtain
  ONE external strict re-reduction (fresh-Fable: "auditability is an L0
  claim until an outsider re-reduces a bundle" — conceded by Codex as
  the cleanest new criticism of the debate); (2) USB-C PD / wall
  cross-check; (3) same-class unit-to-unit CV campaign. None upgrades
  today's claims; each raises the claim ceiling.

REPO-VERIFIED CORRECTIONS (attack round; applied to the review doc):
bundles are gitignored/unpublished (external auditability never yet
exercisable); NO LICENSE file (blocks all external adoption; owner
decision); D-033 strict-validation legacy bypass (absent
summary_provenance skips workload-provenance checks — known tamper
hole, queue row); gating stack is partially exercised (D-014 protocol +
MDE sizing ran on real data; the floor gate itself has never fired);
contamination catches were one human + one automated (not two
automated); Jetson leg is a physical shunt measurement, not a vendor
model — the program's sensor taxonomy is mixed, not uniformly modeled.

DISSENTS RECORDED: fresh-Fable maintains full spine inversion (thesis =
model, not dataset); fresh-Fable's Token-Shape omission overruled;
original Codex-draft optimism on the uniform crossover prior overruled
by its own debate arithmetic.

PROMOTED: D-048, D-049. Queue rows: D-033 bypass fix, bundle-pack
publication prep, split-prep AP-row obligation, PROJECT_STATUS
orchestration-surface trim. Owner items surfaced (not queued as
blockers per scope rule): LICENSE choice; USB-C PD analyzer; external
re-reducer recruit.

## C-021: Advisor status-site live-depth refresh (2026-07-09)

Pointer entry. Full narrative and verification live in
`docs/run_reports/2026-07-09-advisor-status-site.md`; decision policy is
D-051.

Shape: Codex implementation stream over the Lakebed capsule and generated
site, with a separate gpt-5.5-high read-only counterreview before deploy.
The work was intentionally deployment-scoped rather than research-scoped:
make the advisor preview harder to stale, easier to scan live, and deeper
without moving source-of-truth status out of the repository.

Resolution:
- Keep generated static pages as the audit fallback; do not make Lakebed a
  parallel project-status database.
- Add `/api/live-status` as a fail-soft overlay parsed from current GitHub
  markdown for `PROJECT_STATUS.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, and
  `docs/risk_register.md`.
- Expand the generated status cockpit with advisor attention, campaign
  readiness, evidence, and claim-ceiling panels.
- Remove volatile hand-authored counts from the Story page unless they are
  generated or source-linked.

Dissent: none recorded before deploy; counterreview findings, if any, are
adjudicated in the run report.

## C-023: Scientific-rigor review — suite, benchmark, question bank (2026-07-09)

- Date: 2026-07-09. Participants: Claude Fable (lead adjudicator), 4 fresh
  gpt-5.5-high read-only lenses (L1 metrology, L2 benchmark/statistical
  design, L3 question-bank audit — every question individually, L4
  Stanford-PhD-EE advisor simulation), 1 fresh gpt-5.5-high discussion
  instance (D1) arguing the lead's synthesis with doc-verification duty.
- Full record with verbatim lens outputs:
  `docs/reviews/2026-07-09-scientific-rigor-review.md`. Review-only
  session: no code changed, no worktrees (read-only fan-out per
  codex-delegation §Parallel threads).

Question: steelman the methodology, scope, and objectives; does the
project as specced (hardware openly not in hand) stand up to a
Stanford-PhD-EE advisor?

Resolution (lead, with D1 concurrence):

- Today: strong PROVISIONAL methodology; simulated advisor withholds
  final sign-off on specific, curable grounds.
- All blocker-class gaps are software/spec-only: B1 metrological error
  budget + uncertainty propagation; B2 benchmark-level multiplicity /
  analysis registry; B3 canonical RQ registry (bank overgrown, aliases
  unnormalized); B4 frozen capstone headline + minimum-viable-capstone
  contract. With those landed, both models independently answer YES at
  the advisor bar, under the headline "auditable, boundary-labeled local
  LLM energy characterization on named stacks" with split inference as
  gated stretch.
- Design-bearing majors accepted: contrast-level inference replaces
  "intervals separate" (amends D-014 wording when adopted); ordering
  executability before any suite campaign (C-015 rotation promise vs
  sequencing-spec manifest_order — elevated by D1); token-normalization
  contract + stack-identity table; phase-window claim gate; thermal
  proxy honesty; per-backend telemetry-trust caveats + pre-registered
  calibration runbooks.
- Discussion catches (the review system working both directions): D1
  OVERTURNED the lead-accepted C5-1.1 attribution blocker by citing the
  existing C-014 amendment + claims-ladder forbidden language (lead
  verified and accepted — naming hygiene only); D1 reordered the lead's
  pre-hardware work plan (headline first, P2-015 as combined
  floor+calibration+trust+error-budget spec, stats amendment before
  reducer code, campaign packs last behind a registry/linter cut-line).
- Unique catches by layer: L1 error budget + idle-model + phase-gate;
  L2 multiplicity + contrast-rule + ordering gap; L3 registry gap +
  per-question table + coverage gaps (telemetry perturbation, version
  drift, jitter sensitivity, output-token identity); L4 frozen headline
  + MVC contract + stack-identity table; D1 the C5-1.1 overturn + plan
  reorder. Zero-yield layers: none.
- Dissents: none unresolved after one discussion round.
- Queue impact: deliberately NOT applied — the recommended work order is
  input to the user's next planning session (spec fleshing for all
  no-hardware pieces), per the user's two-step directive.


## C-024: Spec-fleshing wave 1 — no-hardware artifact build (2026-07-09)

Pointer entry. Full narrative and verification:
`docs/run_reports/2026-07-09-spec-fleshing-wave1.md`; decisions
D-052..D-055; review inputs from C-023.

Shape: lead-driven, four worktree streams implemented by gpt-5.5 against
the C-023 packet (scope/headline, P2-015 combined floor design, stats
amendment + analysis registry, canonical RQ registry), each with a fresh
read-only counterreview lens, FIX-N rounds for accepted findings, a fresh
final-head pass per branch, a tail-verification pass over post-review
commits, CI, self-merge under the standing authority, and one post-merge
integration review (5 seam findings, fixed same-session).

Dissent: none unresolved. Notable adjudications: R2 estimator kill
accepted (floor redefined as false-effect guard); FH ledger-promotion
blocker resolved by supersession annotation per the history rule, not
rewrite; R4's bank-cited un-merge of C5-W.3 from Q5 overrode the original
C-023 lens's duplicate call.

Addendum (2026-07-09, C-027, MET-001 / REV-12): C-024 records "3 fix
rounds" while its run report records fix units F1-F6 ("6 fix
rounds", counted as 6 in the session total). Clarification: the
records do not conflict — the session ran 3 chronological fix ROUNDS
comprising 6 fix UNITS: round 1 = F1-F4, one per-stream fix pass
after the four counterreview lenses (scope, p2015, stats, rqreg, run
in parallel); round 2 = F5, the p2015 tail fix; round 3 = F6, the
integration fixes (per the wave-1 report's F1-F6 row, "6/6 one-shot
clean", and its yield line "6 fix rounds incl. integration").
Convention going forward: council log counts ROUNDS; run reports may
additionally count UNITS and must label which they are counting.

## C-025: Wave 2 — ultracode workflow build (2026-07-09)

Pointer entry. Full narrative and verification:
`docs/run_reports/2026-07-09-spec-fleshing-wave2.md`; decisions
D-056..D-059; work order from C-023 via C-024.

Shape: first Workflow-orchestrated build (46 agents: 4 codex implement
streams in worktrees -> 2 lenses each with stream-specific angles ->
severity-tiered adversarial refuters: blockers 2, should-fix 1) plus two
lead-driven reinforcement streams (claims linter pulled forward from the
cut-line; RQ-ENERGY-VARIANCE candidate design from Ed's variance
question), then per-stream fix rounds, lead gates (suite + live e2e on
the lead's shell, incl. strict-validating live rotated campaign
bundles), 6 fresh final-heads, a combined tail-verification pass, a
throwaway combined-ref merge + full suite BEFORE merging (C-022 lesson,
first deliberate use), CI, self-merges, and one integration review with
live rotated-campaign interaction checks.

Notable: the design-round-first flow (Ed's directive, folded to
operation-loop §4a) ran on P2-030 — 5.5's design memo ratified with pins
before implementation; zero design rework followed. Codex worktree
commits remain sandbox-blocked (index.lock) despite git permissions —
workflow wrapper agents committed/pushed; lead pathspec commits for
direct codex-run streams. PROCESS DEFECT recorded: the lead ran its
bookkeeping edits concurrently with a workspace-write codex fix round in
the SAME main tree; the fix round's cleanup reverted the uncommitted
bookkeeping (recovered same-session from in-context content) — the
two-writers rule applies to the LEAD as well; bookkeeping waits for tree
quiescence. Dissents: none unresolved.


## C-026: P2-034 broad campaign packs (2026-07-09)

Pointer entry. Full narrative:
`docs/run_reports/2026-07-09-p2034-broad-packs.md`. Design round
ratified with three lead pins (unnamed second-family placeholder;
runtime-held-constant = revision/build-family; smallest
method-transfer suite first for C5-3.5); no new decision-log entries
(pack content rides ratified contracts). Dissents: none.

## C-027: Whole-project council review with gpt-5.6-sol (2026-07-09)

Full record: `docs/reviews/2026-07-09-c027-whole-project-review.md`
(disposition table for all ~80 lens findings, per-blocker verification
lines, deliberation traces). Raw lens/counterreview/examiner outputs
archived under `docs/reviews/c027/`. This entry records only the
genuine deliberation.

Participants: Fable 5 lead; Codex gpt-5.6-sol xhigh (FIRST production
session of the new model; CLI upgraded 0.143.0→0.144.0 mid-session
after the old CLI rejected the model) — 7 read-only lenses + 1
counterreview; 1 fresh-context Fable-tier final examiner. Scope
declaration: all peer passes were STATIC-ONLY and single-model-family —
execution behavior, SSH-path security, and licensing were reviewed by
nobody and are recorded as open debts, not clean.

Positions → resolutions (design-bearing only):

- Legacy-gates framing: lead draft said the six real bundles "failed
  the advertised gates"; counterreview showed D-037 binds from 2M
  onward, so the correct frame is legacy L1 + manual waivers —
  counterreview PREVAILED (the lead's framing would have manufactured
  an ex-post-protocol defense problem).
- Process-restructure staging: lead deferred the machine-readable state
  kernel; counterreview argued deferral leaves the demonstrated drift
  mode active and that policy generation is the harder half —
  counterreview PREVAILED; kernel is Stage 1 (D-063 records the
  reversal).
- Layer-drop rule: lead's "3 applicable sessions, severity-weighted"
  was attacked as reintroducing post-hoc discretion; adopted WITH the
  peer's mechanical-predicate construction (D-061).
- ARCH severity: undifferentiated blocker trio split into immediate
  (zero-window, P2-040) vs NVIDIA-gated (NV-GATE-2) per counterreview.
- Sequential sampling: fixed-n + explicit demotion adopted over both
  status quo and default alpha-spending (D-062); peer confirmed the
  demotion rule is coherent only with its four explicit clauses.

Layer yields (C-027): lenses 8 confirmed blocker clusters + ~60
accepted findings, 0 verified false positives (blocker tier; lower
tiers unaudited); counterreview 3 synthesis blockers (2 were LEAD
errors — the only confirmed review errors this session were the
lead's); final examiner 8 dropped/under-tiered findings + the
validity-threats section, all adopted. Reverse-review layer indicted
the lead's own conduct (empty D-050 manifest, four D-031 direct-to-main
commits) — accepted in full, remedies in MET-001/RETRO-001.

Dissents overridden: none unresolved. Lead notes for the record: ARC-1/2
remain hard acceptance gates at NVIDIA live promotion despite the
severity downgrade.

Calibration (model-version scoping): one promising 5.6-sol batch —
9/9 OK exits, ~28 verified file:line claims all accurate, unprompted
premise correction (5 instances), the counterreview out-argued the lead
twice. NOT a promotion; the pre-registered sealed A/B remains the gate
before delegation-boundary changes.

---

## Index row

| C-028 | 2026-07-09/11 | C-027 adjudication → integration arc under the Fable-lead / gpt-5.6-sol division of labor (this segment: infrastructure wave + PRs #49/#54/#55 + integration window) | PRs #49, #54, #55 merged mid-arc; held wave #50–#53, #56–#58 integration-reviewed and merged (SHA-guarded) after the integration tree caught 38 cross-stream failures pre-merge; follow-up PR #59 opened from the cross-stream review; refuter tier narrowed 2 blockers via contradictory verdicts; delta re-audits caught 2 fresh blockers in newly-reachable paths; claude-codex-report/v1 + codex-run-v3 + WRITE_SCOPE backstop + NEEDS_RULING adopted (D-064); ~57 recorded Sol invocations |
| C-029 | 2026-07-11/12 | Agent-lane triple (SITE-01 / P2-049 / P2-028): three standard-tier Sol pipelines, per-stream lenses, lead bench adjudication of 5 blocker claims (2 confirmed, 1 partially refuted, 1 design ruling, 1 reproduce-first — refuters replaced by lead code-reading where cheaper); trace + calibration table in `docs/run_reports/2026-07-12-agent-lane-triple.md` §Process Trace Appendix (the ONE home; no full entry here) | PRs #61/#62/#63 opened at lead-gated heads; lead-gate unique catch: fix round's `succeeded`-only rule would refuse legitimate `capped` cells (FIX-14; third "fix rounds introduce defects" datum); implementer caught a stale kernel authority pointer (half-right — lead archaeology completed it, `507f600`); process defects logged: WRITE_SCOPE in-prompt requirement (3 rc=64), unintended ULTRA effort on all 13 invocations (config passthrough; TOOL-01), upstream outage killed 3 delta-audit attempts (re-audits owed pre-merge on #62/#63) |
| C-030 | 2026-07-13 | Restart close (continuation of C-029; Ed-authorized merges): delta re-audits on #62/#63 finals + post-merge integration review, all explicit xhigh (effort fix held: 3 sessions ≈ 7.0M tokens vs the prior 13 ≈ 118M); two lead bench fixes with defect regressions; trace in `docs/run_reports/2026-07-13-restart-merge-deploy.md` (the ONE home; no full entry) | #61-#63 MERGED; delta-audit unique catch DRA-001 (equal-but-malformed identity hashes counted as identity evidence — fourth "fix rounds introduce defects" datum, this one surviving TWO earlier review layers); integration-review unique catch XSI-1 (installed-wheel CI ran only --help; now smokes both new fail-closed surfaces); lead-live layer: deploy ACCEPTED 854,349 B / routes 5/5 / freshness clear + cross-thread breakage fix (P2-028 kernel retirement vs gen_state fidelity tests, caught by the concurrent bridge thread's suite run); concurrent Claude↔Sol bridge landed same tree, lead-verified 8/8 protocol + 4/4 tests before commit; PAUSE: comprehensive whole-project audit declared next gate (Ed) |
| C-031 | 2026-07-13 | Bridge v1 (Ed-directed): 3-round Fable<->Sol design discussion held OVER the MCP bridge itself (thread 019f5a67-00f5); Sol out-designed the lead 3x (hard-block leases vs warn-only, path-level baseline manifests vs status digest, split event logs) — all accepted; 5 draft-choices lead-adjudicated; impl + 2 fix rounds + fresh lens + delta re-audit; full record `docs/run_reports/2026-07-13-bridge-v1.md` (the ONE home) | PR #64 MERGED: bridge-protocol/v1 contract + scripts/bridge (atomic hard-block leases — direct fix for the 2026-07-12 cross-thread collision — baselines, 4-verdict scope-check, thread registry) + adapter FAILED-synthesis; lens caught 4 blockers, delta re-audit caught 1 NEW blocker (malformed-override fail-open; FIFTH fix-rounds-inject-defects datum); audit-loop termination ruling: post-fix2 residue lead-verified directly; suite 1358 OK |
| C-032 | 2026-07-13 | Bridge v1.1 (Ed-directed: "fix up the bridge for maximum co-work"): Sol xhigh design consult over the bridge (thread 019f5d1d-b681-7db1-8714-812fdd2f198b; 5 amendments accepted + v1 duplicate-sentinel adapter bug confirmed); ratified spec Sol-implemented; 3 lenses → 3 fix rounds → 3 delta re-audits, finding convergence 13→6→2→1; full record `docs/run_reports/2026-07-13-bridge-v11.md` (the ONE home; no full entry) | PR #65 MERGED `d285989` (Ed named the merge same session after the harness declined agent self-merge): discussion lane, receipt-anchored session-open/close wrappers (session.lock-serialized, write-only in v1.1), tolerant envelope, per-call reverse effort + echo, peer channels + bounded proposal diffs, one-home effort dedup; delta re-audits caught 6+2+1 fix-round findings (sixth/seventh "fix rounds introduce defects" data) incl. two corrections of the lead; suite 1387 OK; CI green on final head 8b96bd4 |
| C-035 | 2026-07-15 | AXI spec-design phase (Ed: "design as many specs as you can with help from sol"; arc opened post-clearance with predeclared deliverable per WO-022 §5a): three parallel Sol spec pipelines (SA xhigh / SD high / SE xhigh), each author -> fresh counterreview -> fix round(s) -> delta -> lead termination; ~14 Sol sessions ≈ 71.2M tokens (est.); full trace in the 2026-07-14 run report §AXI spec-design phase | Specs landed `1464c93`/`d2bd5ee`/`3b5c4bf`: SA burst-decode contract (implementation-ready; honest frozen-arm goldens after the counterreview refuted byte-identical vs actual code; deterministic anti-top-up ledger), SD pair scorecard (four-option D-016 decision box for Ed; forced-continuation memory probe), SE six AP drafts (estimand demotion on AP-REASON-VARIANCE; union-bound + Markov-quantile floor guards; 21 PROVISIONAL cells with named triggers); 30+ counterreview findings fixed pre-landing; 3 benign lease-close artifacts pending Ed batch adjudication |
| C-034 | 2026-07-14/15 | Audit fix-wave resume + close-out (Ed's AXI handoff §0.2 sequencing; full record `docs/run_reports/2026-07-14-audit-resume-axi.md`, the ONE home): per-order cadence Sol high/xhigh implement → fresh checker → fix rounds → lead gate; 28 Sol sessions ≈ 251M tokens (ARC HARD crossing recorded in the refreshed WO-022 receipt — gate-closing work, policy landed mid-arc); ULTRA comparison audit (intended, pre-declared) + xhigh integration review + Fable completeness critic + C-033 coherence council | S1 closed (WO-010 NEEDS_SCOPE grant, WO-011 checker-FAIL→fix→delta-PASS), S4 closed (WO-019 PASS-0-findings; WO-031 3-major fix round), WO-027 fix round, WO-021 xhigh 3-phase w/ 8a receipt + 4-record-loss BLOCKER migration, WO-022 verbatim landing; integration tree `impl/audit-integration`: 2 unique integration catches (capsule budget union breach; D-068 vacuous-green surfaces) + ULTRA's 2 blockers/20 findings triaged per Ed's substance-over-ceremony ruling (7 fixed `913a2a6`, 4 bench, 5 queued, rest dispositioned §8.5); D-043 closure (17 lines + 6 lead decision-log amendments); critic's 3 gaps closed same session; suite 1532 OK at `f8f0f92`; PR to main awaits Ed's adoption merge; 3 lease adjudications Ed-approved after classifier refused lead self-approval (correctly, all three times) |
| C-033 | 2026-07-14 | AXI intake council (Ed-directed via `docs/axi-handoff.md` + Ed's batched §5 answers this session): short recorded Sol high read-only coherence review of drafted D-066..D-070 (outcomes Ed-directed, not re-decided; consult ran over the audited CLI path because the MCP server is unavailable in this headless session; prompt/response tracked at `docs/process_traces/2026-07-14-c033-axi-consult/`) | Sol verdict DISCUSSION: outcomes authorized, Ed's four D-067 amendments honored; 6 coherence corrections identified and ALL lead-accepted before commit: explicit supersession of the D-058 token-normalization Primary Metric clause (contract text assigned to S-A, keeping S-0 docs-only), dual-basis-capture bundle-state definition (successful idle-eligible request-level; nullable semantics preserved), D-032 gross-only phase semantics named, deploy convention re-attributed C-012→C-013, registry source homes corrected (C5-* bank vs C-023-*/RQ-* registry per D-055), `request_id` pinned to `events.jsonl` `metadata.request_id` with new-version-only reducer dispatch, D-064 duplicate/mismatched index rows cleaned; remaining deploy-instruction surfaces routed to WO-031 + S-0 |
| C-037 | 2026-07-17 | Window-A execution + wrap arc (Ed: floors-first overnight -> advisor deadline -> site rebuild -> exploratory breadth; full records: the two 2026-07-16/17 run reports, the ONE homes): four-failure shakedown story (stale-bundle reuse, wallpaper idle contamination caught by sentinel, 34.6ms trace-boundary bracket via two live-bundle triages, stale-lock exit-0 wart) -> canonical PASS; 248-line/222-bundle floor campaign verified by 8-agent ultracode extraction; advisor brief + README-first site + Learn guide (Ed deployed); exploratory 9-bundle block; DSpark/DFlash feasibility confirmed; D-071..D-075 recorded | PRs #72-#75 merged under D-072 standing authority; delta re-audits caught blockers twice more (10th datum incl. lead-pinned formula defect); fold-in round's refusal caught a forced-report placeholder trace; scope enforcement caught the lead's own stray file (adjudicated benign); floors: request 0.527/0.052 J, phase 1.477/0.786 J, ABBA comparative w/ flagged tail drift; exploratory gross suite: OLMoE ~229 J vs Qwen3-4B ~362.8 J vs 122B ~1072 J (exploratory-labeled) |
| C-036 | 2026-07-16 | Resumption + no-hardware batch (Ed: audits in a workflow + "handle the merge yourself if all is well... get the project ready for my quiet mac"; full record `docs/run_reports/2026-07-16-resumption-nohw-batch.md`, the ONE home): ultracode readiness workflow (4 Sol-high audits + severity-tiered refuters) BEFORE work selection; then 4 streams (SPLIT-AP xhigh contract tier, SITE-02 high standard, AXI-SB xhigh spike, AXI-SD Fable web-verification); every fix round delta-re-audited; three self-merges under Ed's in-session delegation, each with the full D-031-amended gate | PRs #67 (`7593259`, AXI-SA + CI portability fix after the audit caught red CI), #68 (`2778ed2`, SITE-02 — D2 step verified EXECUTED in the CI log), #69 (`9db4546`, SPLIT-AP freeze) merged; integration review 0 cross-stream defects, merged main 1630 OK; kernel closures 51→48 IDs; AXI-SB live probes (lead-run, B∈{2,4}) → verdict `supported`, Mac C5-2.2 leg mint staged on `impl/axi-sb` (effective on its merge); delta re-audit caught a LEAD-pinned predictor defect (8th fix-rounds-inject-defects datum, first lead-authored); AXI-SD memo: OLMo pair d_active 0.0016 + 8GB-fit may moot Option A's premise, Qwen3 pair confirmed-fails G10 (17.17 GB) |
| C-039 | 2026-07-28 | Mint-implementation session (Ed: resume per RUN_STATE, then "merge on green + start the mint consult"; magistrate topology; full record `docs/run_reports/2026-07-28-floor-mint-implementation.md`, the ONE home): PR #87 gauntlet (2 Sol xhigh lenses + 5 Sol high refuters + 1 Opus contract refuter, lieutenant-directed), E4 fix + CLEAN delta re-audit, D-081 parser ruling (Ed, async question), Sol xhigh mint design consult (3 DISAGREEs sustained -> D-082), 7-stage xhigh implementation, suite-pruning consult (0 removals clear D-061) | PR #87 MERGED `058c918`; `impl/mint-tool` pushed unmerged (review owed); C1 SPLIT (Sol nit vs Opus should-fix) magistrate-synthesized to should-fix, closed via ratified Q4; 5 broken-wake incidents -> tracked-poll pattern folded to codex-delegation; lieutenant self-flagged 2 retracted fabricated verdict narrations (mechanism removed); concurrent-session force-push anomaly flagged to Ed; **ADDENDUM at the end of this file** records the 2026-07-29/30 continuation (FIX-6..9 gauntlet, three cold gates with paired Opus contract-lens refuters, mint #1, the 7B floor window; rulings D-083..D-088; D-088 recorded in the same-day close-out); **ADDENDUM II** records the 2026-07-30/31 escalation consults (cooldown-join design consult → D5-J/D-089; contrast-window recovery consult, the first trigger firing inside a measurement window) |

---

## Full entry

## C-028: C-027 adjudication and integration arc — infrastructure wave, PRs #49/#54/#55, and the integration window (2026-07-10/11)

Full record: `docs/run_reports/2026-07-11-c028-continuation.md`; binding
rulings: `docs/specs/c027/ADJUDICATION.md`. No tracked
`docs/process_traces/` artifact is present in this checkout; the run report's
aggregate invocation record is therefore the durable evidence available for
this arc, and D-064 governs future tracked event streams. This limitation is
recorded rather than repaired with an invented pointer.
The arc's earlier segment (adjudication rounds, PRs #41–#48) is
recorded in the CP-5/checkpoint records and stop-card history; this
entry records the 2026-07-10/11 continuation.

Participants: Fable lead; gpt-5.6-sol as implementer, reviewer,
refuter, auditor, and design consultant across ~57 recorded
invocations. The lead retained worktree/merge authority, every final
diff gate, all live verification, and bookkeeping.

Scope of this segment: PR #49 (NV-GATE-2 code-now + flake
root-causes) merged `1b0f1f6` + `10e0ad2`; PR #54 (P2-041 vetted
rebuild from the RED-tranche triage recipe, review + fix round +
delta review) merged `69a3393`; PR #55 (P2-044 idle dependence /
HAC / ESS, design-consult-first, review + fix round) merged
`56d103e`. At the Ed-directed pause (stop card checkpoint #4 +
amendments) PRs #50–#53 and #56–#58 stood open and lead-gated with
the resume order pinned; after resume, the integration tree
(`c028-integration` @ `190a0fc`, main post-#55 + 7 branches) caught
38 cross-stream failures, the fix round + cross-stream review
cleared them, and the full wave merged SHA-guarded (#50, #51, #52,
#53, #56, #57, #58 — P2-037 last), with final main verified green
and content-identical to the reviewed tree; follow-up PR #59 (from
the cross-stream review) is under review and DOC-008 rounds remain
in flight. Delegation infrastructure landed on main: adapter,
codex-run-v3, usage guard, scope backstop.

Closeout amendment (2026-07-11): C-028 is **CLOSED**. PRs #41-#58 are
merged; current main's canonical suite is 1,220 OK (`skipped=10`) and the
corpus gate is 6/6. PR #59 remains open with a 1,224-test green worktree
replay (`skipped=12`), and `impl/doc008-kernel` is pushed awaiting PR. These
open follow-ups do not reopen the card. Every Window-A software gate and
P0-003 are satisfied; quiet-machine execution with Ed remains deliberately
separate from landed-software status. NVIDIA/Orin protocol pins remain
PROVISIONAL pending live evidence.

Layer structure: Sol implementation sessions (xhigh; 2 ultra for the
p2041-vetted composition and the P2-037 engine) → review lenses
(contract + semantics per stream) → severity-tiered refuters (2 per
blocker) → independent post-hoc audits (P2-037) → delta re-audits
after fix rounds → lead gates (live runs, arithmetic checks, final
heads, CI) → cross-stream integration tree before each merge.

Unique catches per layer (D-061 evaluation record):

- **Sol merge review:** caught the lead's own merge-resolution
  error — the branch's updated P2-005 row silently lost by a
  whole-file `--theirs` checkout during the #49 conflict
  resolution; repaired as a proper 3-way merge (`13f6c9e`). Only
  layer to catch it.
- **Refuter tier:** narrowed 2 blockers via CONTRADICTORY paired
  verdicts — P2-041 B1 (contract refuter confirmed, reachability
  refuter refuted the broad form → landed as the narrowed shared
  fail-closed cooldown verifier, `f2c4701`) and P2-037 F1 (design
  vs repro refuters split the same way → F1 narrowed before the
  fix round). The disagreement itself was the signal; neither
  single refuter would have produced the narrowed form.
- **Delta re-audits:** 2 fresh blockers in paths newly reachable
  only after the fix round (P2-037 delta re-audit:
  blocker=2/should-fix=3), plus the recurring symlink pattern —
  cooldown provenance `Path.resolve` unwrapped against symlink
  loop/OSError, wrapped fail-closed with a cross-version
  regression test (`5f1f161`). Neither finding existed in the
  pre-fix tree; the re-audit layer is what sees post-fix
  reachability.
- **Lead gates:** P2-044 F1 cadence arithmetic verified directly
  (all-intervals population; binding Qwen-r3 values asserted
  exactly: median 0.1199250625, ratio 1.0581313969 — `dc1ab95`);
  live NV-5 localhost gate 3/3 OK closing the open lead gate on
  #49 (`10e0ad2`); live doctor run. All three are
  lead-live-only — no static layer could produce them.
- **Integration tree:** 38 pre-merge cross-stream test failures
  caught at the combined head, dominated by REPRO-002's
  fail-closed environment/inventory checks meeting post-cut fields
  from sibling streams. Zero of these were visible in any single
  stream's green suite.
- **Enforcement layer (scope backstop, live):** 2 bytecode
  false-positive firings tuned same-day; NEEDS_SCOPE compliant
  stops ×3 (p2037 fix round, doc008 ×2) — each returning the
  correct paths where the lead had guessed wrong.

Scope enforcement fired in production: two sessions (p2043-impl,
p2044-fixround) exited SCOPE_VIOLATION with work preserved in
evidence bundles, not landed; one wrapper crash (lead in-place edit
of the installed runner mid-run) was recovered via a lead-authored
recovery row rather than a mutated record — both behaviors are now
ratified in D-064.

Rough spend (from the two manifests + local usage accounting;
estimates, not billing truth): 2 ultra sessions ≈ 100M tokens
(p2041-vetted composition, P2-037 engine); 53 recorded xhigh
invocations (14 v2-manifest + 37 v3-event-stream + 2 transition-era
rows) — local 24h accounting shows 50 xhigh sessions ≈ 171M tokens;
2 high (both FAILED rc=1 resume attempts, work recovered in later
sessions) ≈ 40M. Fable lead: ~1.8M generation / ~14.8M billed-ish /
~570M cache reads. Two v3 sessions (doc008-r3, pr59-review) still
RUNNING at the manifest snapshot.

Spend snapshot addendum (2026-07-11 ~20:00Z, `codex-usage` 24h
window, arc-close truth for the table above; estimates, not billing):
59 Sol sessions / 330.6M tokens / ~17.5h session time — xhigh 55 ≈
190.4M, ultra 2 ≈ 100.3M, high 2 ≈ 40.0M (both FAILED). Composition
(measured from raw session records): ~97.4% of Sol input is cached,
output ≈ 0.37% of volume. API-list-price equivalent (GPT-5.6-sol
$5/$30, cached $0.50; Fable 5 $10/$50, cache reads $1): Sol ≈ $240,
Fable ≈ $810 — combined ≈ $1,050 for the recorded arc; upper bound
≈ $2,300 counting all local Codex sessions (includes non-manifest
sessions; resume rows may double-count). Note the inversion: Sol is
~180x the token volume but Fable is ~3.4x the cost — cache reads
dominate the lead's footprint. Snapshot convention now standing in
the council skill §Recording + instrumentation.

Process artifacts adopted this arc (ratified as/alongside D-064):

- **claude-codex-report/v1** — canonical machine-parsed session
  report envelope; run_finished rows record parse validity, finding
  counts, verification counts, scope flags.
- **codex-run-v3** — append-only event-stream manifest
  (run_started/run_finished/run_consumed), retry-with-resume,
  lead-authored recovery rows on wrapper failure.
- **WRITE_SCOPE backstop** — post-run diff vs declared scope; exit
  77 + evidence bundle on violation; NEEDS_SCOPE prospective-only
  expansion (AGENTS.md precedence section, `9ca89cc`).
- **NEEDS_RULING** — any blocking non-delegable decision
  early-returns a structured question instead of a guess
  (`31b3f5e`); usage guard + usage-pressure mode active.
- **Design-consult-by-default** — Ed-prompted global-rule
  amendment; exercised for P2-044 (HAC/ESS design consult,
  `827df12`) before implementation.

Dissents overridden: none unresolved. The P2-041 RED tranche
(ultra round deleting P2-038/P2-040 wholesale) was not landed or
argued — it was triaged per-file and rebuilt from main under three
Ed-approved C rulings (`96e10bd`, `750f7d0`).

Calibration note (model-version scoping, per C-027): the refuter
contradictory-verdict pattern produced correct narrowings twice;
the two scope violations and one thin-output ultra warning are the
arc's recorded 5.6-sol failure modes. Sealed A/B remains the gate
before any delegation-boundary change.

## C-043: D-078 P0 instrument-repair close-out session — round-8 landing, round-9 final confirmation, sign-off (2026-07-22)

Shape: lead resumed the paused arc cold from scratchpad pointers; collected
the checkpointed Sol round-8 fix wave; §C-028 delta re-audit (3 fresh
read-only Sol lenses over a shared packet → 8 xhigh refuter verdicts,
blockers 2 refuters with distinct lenses); Sol xhigh round-8b fix wave under
enforced WRITE_SCOPE (one NEEDS_SCOPE early-return, lead-ruled, fixture fix
applied at the bench); bounded 8b delta re-audit; lead full-suite gates
(2081 → 2088 passed, 0 failures); commit `040ca3a`; round-9 FINAL
confirmation (Sol xhigh review genre); CR9-1 adjudicated as registered
limitation L1 per the loop-termination doctrine; close-out `debc6d2`;
PR #79 opened for Ed-named merge.

Layer catches (unique):
- Sol review lenses: A1 (v3 claim-eligibility contract divergence),
  B1 (ClockStamp physical-sanity gap → understated B_fiducial ~3 µs),
  C1/C2 (boundary float, OverflowError escape), C3/C4 (test-wiring gaps).
- Sol xhigh refuters: killed A2/B2 outright (both plausible, both wrong —
  A2's "legacy records break" was self-invalid synthetic-only; B2's
  stale-vs-invalid relabel would have broken a ratified distinction);
  narrowed C1 to a registered nit; split on A1 (contract-confirmed,
  reachability-refuted) — lead synthesis: pre-existing defense-in-depth
  hardening, not a round-8 regression.
- Round-9 confirmation: CR9-1 (floor artifacts self-attesting) — the only
  finding of the round, repro-backed, lead-reproduced at the bench.
- Lead unique: false-attribution triage of the 8b audit's two "blockers"
  (both were the lead's own authorized bench edits); the L1 adjudication.

Failure modes recorded: (1) upstream cyber-content filter killed 3/8
refuters mid-run on adversarial phrasing ("malformed/tamper/escape") —
rephrasing as data-quality QA of our own instrument recovered all three
(route: keep refuter briefs mechanism-neutral); (2) lead bench-edited the
worktree while an enforced-scope Sol session ran in it → false
SCOPE_VIOLATION attribution + resume-registry loss (rule: no lead edits in
a tree with a live enforced-scope session); (3) the known xhigh review-genre
null-final-message mode recurred on round 9; the documented bridge-resume
recovery worked first try.

Dissent recorded: the 8b delta auditor's should-fix (OverflowError
normalization also reaching v1 replay error behavior) was overridden by
lead ruling — frozen-replay doctrine protects computed semantics of
parsable artifacts, not crash reproduction on impossible inputs; the
reducer's structured-failure contract governs all protocols.

## C-044: NEG-8 estimand debate — peer disagreement adopted, Ed ratification (2026-07-24)

Ed directed a formal cross-model debate on the clause-10 ruling before
ratifying. Shape: lead position paper + explicit license and request to
disagree; one xhigh peer round evaluating five design options plus a
peer-proposed sixth; lead adjudication; plain-language synthesis to Ed;
Ed ratified the amended design with recorded guardrails (decision log
clause-10 addendum). Yield: the peer's structural correction (anomaly
screen must not erase drift from the claim budget) was adopted — the
second recorded case of invited peer design judgment beating the lead's
ruling. The debate also surfaced one gap neither model had specced
(drift-bound freshness horizon — prompted by Ed's own risk question) and
one open science question (a7-vs-a5 prefill floor scatter, 3x).
Calibration note: invited-disagreement debate briefs (steelman each
option, demand failure modes + examiner view) produced markedly higher
design yield than review-shaped prompts; adopt as the default shape for
estimand/contract rulings.

## C-045: NEG-8 screen+budget audit gauntlet — a new refuter pairing under A/B, four audit rounds, PR #85 (2026-07-24/25)

Shape: the Ed-ratified SCREEN + BUDGET wave (D-078 clause 10) was taken
through four adversarial audit rounds (fresh read-only Sol per round;
rounds 1–3 xhigh, round 4 high) with per-severity refuter tiers using a
NEW pairing under evaluation — **Opus-contract + Sol-execution distinct
lenses** (Ed-directed A/B; now the recorded default per the
instrument-mix-authority memory). Three Sol fix rounds (xhigh, xhigh +
a high alignment pass, high) plus lead bench fixes closed the findings;
two lead-owned decision-log addenda were written at the bench between
rounds. Commit stack on main(`125a48d`): `b120d07` wave → `69b65e5`
addendum 2 → `ad75542` fix round 1 → `315810a` addendum 3 → `a5a7acf`
capsule trim → `907ee58` fix round 2 → `dbf6339` fix round 3 →
`19e15d9` assertion restore → `60b12af` capsule pagination →
merged `c3e2647` (PR #85, 56 files, +6012/−439).

Layer catches (unique):

- **Auditor (fresh Sol, per round):** found real mechanisms in every
  round — round 1: estimand-dispatch downgrade (row shape selects the
  legacy gross-only evaluator), allowance fail-open (missing allowances
  silently become no allowance), anchor-gate bypass on the
  existing-bundle re-verdict path, and the refusal-registry gap (the
  authoritative registry test actually failed on
  `anchor_fallback_member_unusable`); round 2: coordinated-downgrade v2
  (strip basis *and* the whole drift group together) and the
  mock-label seam (`telemetry_source="mock"` defeats both dispatch and
  the anchor gate); round 3: TypeError on malformed basis values,
  telemetry-triangle downgrade into the frozen arm at the whole-window
  barrier, and loss of nonempty positive-path integration coverage;
  round 4: two omitted assertions in the replacement companion
  (nonempty affected-contrast set, `n == 5`). BUT it severity-inflated
  repeatedly — of 7 blocker-tier claims across rounds 1–2, refuter
  synthesis sustained 3–4 at tier (round 3 and round 4 produced no
  blockers at all: three should-fix, then one).
- **Opus-contract refuter (unique):** F2 collapse (the "broken frozen
  replay" blocker rested on a misreading of the freshness addendum's
  scoping — landed as a documented superseded gross-only wire, not a
  code fix); F6 refutation (condition-level distinctness was already
  contract-discharged at the consumer boundary); G1 re-price (the
  full-strip variant is a subclass of registered limitation L1, whose
  closure is queued as FLOOR-BIND-01, not a fresh blocker); G2
  re-price (the ratified non-mock carve-out plus D-030's
  strict/raw-evidence binding bound the exposure); blast-radius
  refutation of the auditor's proposed G2 fixture fix (strict
  validation binds backend raw evidence, so the naive fix breaks
  legitimate fixtures); **A1 terminal-mock-bar gap — the session's best
  catch**: an *honest* mock member could reach claim evidence with all
  mock-exempted barriers disabled, no attacker required; the NEG-8
  sentinel route on round-3 F2 (the one route with no downstream
  catch); and the F3 fixture-fix refutation (a production-promoted
  fixture cannot be strict-valid — use a patch idiom instead).
- **Sol-execution refuter (unique):** discovery of the
  coordinated-downgrade *variants* (strip the drift group and restore
  the headline floors and the record validates clean — reproduced on
  the repo fixture, gate `20.799350577898302 → 20.399350577898304`,
  exactly the fixture's 0.4 J allowance; asymmetric removal from the
  comparative record alone also validates clean); the G2A adjacent
  blocker (the reduce layer independently trusts metadata/summary
  mockness in the environment and CPU-admission barriers, so fresh
  re-reduction reproduces the forged exemption and strict
  stored-vs-fresh comparison is not a backstop); identification of the
  authoritative mockness source (custody-bound
  `config().hardware_target.telemetry_backend`, bound through
  `metadata.config_sha256`); the `mock:*` tagged-source class caveat
  (`axi_valid_burst` config `mock` vs summary `mock:target` — compare
  backend *class*, not raw strings); and every runnable probe,
  including the estimand-flip demonstration (`mock` → no refusals vs
  `powermetrics` → `whole_window_verdict_provenance_invalid` on
  identical evidence).
- **Lead (unique):** the two D-078 clause-10 registry addenda (2 and 3)
  — component-7 anchor-fallback gate ruling derived from the a7-vs-a5
  prefill-scatter root cause (a7's 11.85 J "floor" was one
  fallback-anchored member, r03; true floor ≈ 3.3–3.7 J), and the
  terminal mock bar; severity synthesis on the split verdicts (kept F4
  at blocker priority on imminent-use grounds against the contract
  refuter's downgrade); the capsule shard-budget trim (`a5a7acf`) and
  the pagination ruling that followed (deterministic `D-NNN`
  pagination + D-076 artifact-cap redirects); the battery-flake
  adjudications; and the bench fixes (registry clause, the fixture
  metadata line that blocked Sol's canonical run, the round-4
  assertion restore).

Rough spend (estimates, not billing truth): the gauntlet proper (audit
round 1 onward) recorded 11 distinct Sol wrapper invocations — 4 audits
(3 xhigh, 1 high), 2 execution refuters (both high), 3 implementation
rounds (xhigh; xhigh + a high alignment pass; high), 1 capsule session
(xhigh), plus retry attempts on two of them; counting the same day's
pre-audit wave, fold, fold2 and run-book sessions brings the day's Sol
total to ~15. Four Opus agents: three contract/design refuters (~96k /
120k / 144k tokens) plus one dictated-fills drafting/verification agent
(~115k) — the latter caught five material errors in the lead's own
dictation of this entry, including the effort-tier discrepancy ruled on
below. Lead orchestration on top. The
`codex-usage` ledger reads all zeros for the 5h and 24h windows ("local
quota signal unavailable in referenced session logs") — the feed is
suspected broken, so no token-volume snapshot is recorded this session.

Verdict: **the Opus-contract + Sol-execution pairing changed the triage
outcome in every round it ran** — it collapsed one blocker outright
(F2), re-priced two (G1, G2), refuted two proposed fixes before they
landed (G2 fixture, F3 fixture), and produced one blocker the auditor
never saw (A1 terminal mock bar). The two lenses split on G1/G2 (Sol
sustained both at blocker; Opus re-priced both) and the lead synthesized
rather than majority-voted, per §C-028. Adopted as the default
blocker-refuter shape; memory and skills to be updated by the lead.

Dissent recorded: on F4 the lead overrode the contract refuter's
downgrade and kept blocker priority, on the grounds that the
anchor-fallback replay path was about to be exercised by the next
window's re-verdict. On G1/G2 the lead implemented both fixes despite
the contract lens's re-price, treating the re-price as a scope
argument (what is *newly* broken) rather than a licence to defer.

Calibration note: the auditor layer's yield is real but its severity
calibration is not — four consecutive rounds produced findings worth
fixing while its blocker tier held at roughly half strength. The
refuter tier is what converts that into correct triage; running a
single-lens refuter would have inherited the inflation.

Effort-tier ruling (lead, flagged by the drafting agent's verification
pass): the execution refuters ran at `high`, not the
adversarial-review skill's `xhigh` default — deliberately in round 1
(Ed's A/B spec named "sol high") and carried into round 2 for
comparability. The A/B verdict therefore stands on high-tier refuters,
which is the STRONGER form of the result: paired distinct-lens
refuters at high changed triage outcomes that single-lens xhigh
refuters have historically missed. Ruling: in the paired-lens shape,
`high` is the default refuter tier; reserve `xhigh` for single-refuter
verification or judgment-dense standalone audits. The lead will amend
the adversarial-review skill's effort note accordingly.

Scorecard (dispositions per docs/orchestration.md): 20 findings raised
across 4 audit rounds incl. refuter adjacents. Accepted-and-fixed in
PR #85: 13 (r1 F1/F3/F4/F5/F7; r2 G1/G2/G3 + adjacent A1 terminal mock
bar; r3 F1/F2/F3; r4 F1). Re-priced by refuters before fixing: 4 of
those (r1 F4 blocker→should-fix; r2 G1/G2 blocker→should-fix; r1 F2
blocker→docs-only, landed as contract clarification). Rejected /
non-obligating: 2 (r1 F6 contract-refuted; r2-A2 traced not-reachable,
defensive comment only). Queued: 4 → kernel row CUSTODY-HARDEN-01
(G2A reduce-layer label trust, drift-bound seal authentication, dead
no-freshness accommodation, artifact_schema_invalid mislabel);
full-strip custody discrimination remains inside pre-existing
FLOOR-BIND-01/L1. Owners: all fixed items closed at merge c3e2647
(lead-verified); queued items owned by the kernel rows named above;
no open finding without an owner.

---

## C-038: FLOOR-LABEL-01 gauntlet close + quiet-window collection — an instrument-mix re-proportioning, a lost quiet window, and two exit codes that lied (2026-07-25/26)

Shape: finish the FLOOR-LABEL-01 gauntlet (D-078 clause 11 — labelled
attribution-limited floors, unblocked by CAL-REBRACKET-01 / PR #86) and
then spend the quiet-Mac window collecting three measurement windows.
Lead instrument: **Opus 5 (1M context), effort `high`, confirmed by Ed
via the interactive `/model` command** (the TUI banner disagreed; see
`docs/process/model_allocation_ledger.md` §6 A-10). Mid-session Ed
**re-proportioned the instrument mix**: Opus 5 subagents become the
primary delegated lieutenant, Fable is consulted when genuinely needed,
Sol remains the execution workhorse, and the lead adjudicates rather
than performing the labor. The standing dictate is recorded in the
`instrument-mix-authority` memory and in the ledger §2 — this entry is
the first session run under it.

### Layer catches (unique)

- **Opus 5 contract lens** (subagent; ~164k tokens, 50 tool uses,
  ~11 min). Verdict **"COMPARATIVE COVERAGE: COMPLETE"** — it traced
  the labelled path end-to-end for comparative (ABBA) cells through
  extraction → canonical floor record → transport group → resolution →
  claim evaluation → final artifact. 4 should-fixes, 4 nits. Unique:
  (a) the `_combined_floor` **key-sniffing heuristic** misattributes
  point-floor diagnostics for a *partially* attribution-limited
  transport group, publishing one cell's repeatability numbers under a
  different cell's ID — and the same heuristic is mirrored bug-for-bug
  in `artifact.py`, so validation recomputes the identical wrong answer
  and it ships (`joulewise/analysis_engine/__init__.py:192`
  `_combined_floor`, verified on `main`); (b) `floor_conditions` proxies
  soleness through a **stale field that post-construction mutation does
  not clear** (`joulewise/floor_extraction.py` on `impl/floor-label`);
  (c) **ratio-unit floors publish a J/token claim floor beside
  joule-valued diagnostics**, making the diagnostic read ~150× larger
  than the floor and inverting exactly the relationship the label exists
  to communicate; (d) **no assertion pins the labelled fields on a
  comparative extraction row** — while 80 ABBA members were about to be
  collected against that path. It also flagged that
  `scripts/build_site.py` and `scripts/build_capstone.py` contain
  **zero** references to the new fields (lead-verified on
  `impl/floor-label`: zero hits for `attribution_limited` /
  `floor_label` / `labelled` / `floor_conditions` in both).
- **Sol xhigh independent audit** (fresh, read-only, ~23 min):
  1 blocker + 1 should_fix. Unique: a **runnable probe (V3)**
  demonstrating that the same comparative blocks minted **without**
  admissible half-widths validate clean via `validate_floor_artifact`
  and yield `floor_gate` **5e-324 J** versus **2.6484 J** with widths —
  an artifact that licenses any effect at all. The lead **adjudicated
  this blocker DOWN to registered limitation L1**
  (`docs/decision_log.md` clause 8, confirmation round 9, 2026-07-22 —
  clause header at l.4407, L1 registered at l.4421), which already
  describes exactly this substitution exposure. Sol was a fresh reviewer
  with no knowledge of L1, so **re-finding it was correct reviewer
  behaviour**, and the probe is the **first concrete demonstration** of
  a limitation that had until now been argued only on paper. Recorded
  with the adjudication: FLOOR-LABEL-01 **modestly WIDENS L1's blast
  radius**, because attribution-limited cells that previously refused
  (and were therefore sterile) now publish.
- **Sol xhigh diagnosis** (clock anchor, ~17 min): root cause at **high
  confidence** — transient **wall-clock-versus-monotonic slew exceeding
  the governed 5 ms anchor ceiling**
  (`MAX_WALL_MINUS_MONOTONIC_SPAN_S = 0.005`, gate at
  `joulewise/uncertainty_evidence.py:367`, detail code
  `wall_minus_monotonic_span_exceeded` at l.369): **5.544 ms
  (≈ +110 ppm)** and **7.769 ms (≈ −158 ppm)**. It **corrected the
  lead's hypothesis** by establishing that the failing members' shorter
  duration was a *consequence* of reduction, not a cause. It also
  **correctly refused** to attribute the adjustment to macOS `timed`,
  marking it UNKNOWN because `joulewise/environment.py` assigns
  `limited_without_admin` unconditionally (assignment at l.908, inside
  `_probe_clock_sync` at l.904) — i.e. the field cannot distinguish
  "not synchronising" from "we lack the privilege to see it".
- **Fable adjudication** (21k tokens, **zero tool uses**, 108 s),
  consulted on the lead's own process failure. It **corrected the
  lead's self-diagnosis**: the lead's proposed "act-anyway deadline"
  rule was *not* the right generalization, because with a working wake
  mechanism the information-block would have cost **17 minutes** — the
  10-hour loss is fully explained mechanically, not by a missing
  deadline policy. It then named the underlying disposition: **the lead
  applies rigorous verification to WORK PRODUCTS but exempts its own
  PREMISES ABOUT THE ENVIRONMENT.** Rule set produced: **R1** turn-end
  invariant (end a turn only with the work complete, or with a
  harness-registered wake source named explicitly); **R2**
  quiet-window dominance, with a stop-loss and a heartbeat that checks
  for an in-flight measurement before acting; **R3** premise labeling.
  It identified failure modes the lead's own rules missed — notably
  that **more wakeups can contaminate a live measurement**. It
  recommended **no demotion**, explicitly arguing against its own
  promotion on the grounds that it would operate the same harness with
  the same wake semantics.
- **Lead (Opus 5) bench catches:** detected that its own suite
  verification was **worthless because it piped output through `tail`**,
  which discarded the summary line and masked the real exit code behind
  tail's; **adjudicated Sol's blocker to L1 by reading the primary
  source** rather than accepting the delivered severity; chose **full
  restart over resume** for window C because resuming would mint a
  second pre-calibration and `latest_calibration()` would select it,
  silently breaking the pre/post bracket; **refused to raise
  `--max-failures`** when doing so would have "fixed" the failures by
  accepting corrupted members; and hand-verified that the refactored
  dominance predicate reproduces both prior inline gates for absolute
  and comparative **before either reviewer reported**.

### Lead errors (recorded plainly)

1. **The lost quiet window — the most expensive process error of the
   campaign.** The lead launched the Sol clock diagnosis with
   `nohup … &`, i.e. **outside harness tracking**, and then ended the
   turn "holding until the diagnosis lands". No wake could fire. The
   Mac never slept (`pmset -g log`), and **~10 hours of open quiet
   window were lost** — enough for both remaining collection windows.
   This is the failure Fable's R1/R2 answer.
2. **Over-read run-book §1** to mean the lead must not launch
   measurement windows. Corrected by Ed.
3. **Asserted Ed's session model as fact** while the TUI banner said
   otherwise; `/model` resolved it to Opus 5 (1M). The banner was
   wrong — but the lead's *certainty* was unwarranted either way.
4. **Three failed `codex-run-v3` invocations** from guessing at the
   interface instead of reading the error. The actual cause: the
   literal in-prompt `WRITE_SCOPE:` line must be **valid JSON**.
5. **The FLOOR-LABEL-01 fix round was launched without a sandbox
   flag**, so it defaulted to a **read-only workspace**; `apply_patch`
   was rejected and the session **did no work**. The wrapper still
   **exited 0**, and only the governed report envelope
   (`status: blocked, completion: none`) revealed it.

**Generalization adopted this session (from errors 5 and the `tail`
catch above): EXIT STATUS IS NOT EVIDENCE OF WORK DONE.** Twice in one
session an exit code masked a non-result — a wrapper returning 0 over a
blocked, read-only Sol session, and a test suite whose summary and exit
status were both swallowed by `tail`. The evidence of work done is the
**governed report envelope** (`status` / `completion`) for delegated
runs and the **suite's own summary line** for local runs. Never a shell
exit code, and never a truncated stream. Mirrored into
`docs/process/model_allocation_ledger.md` §6 A-14, because it bears
directly on how delegated work must be verified.

### Collection outcomes

- **Window B** (`04_phase_prefill_abba`): **59/59 members, zero
  failures, zero waivers, zero missing** (lead-verified: 47 campaign
  members + 12 reference-corpus members across
  `runs_window_b_20260726/` and `runs_window_b_20260726_bound/`; every
  `collection.categories` block reports empty `failed` / `missing` /
  `waived`). Pre-calibration **07:04:09Z**, post-calibration
  **10:15:52Z**, `measurement_complete` **10:15:52Z** (lead-reported;
  the two calibration bundles' `sampling_stopped` events are at
  07:03:57Z and 10:15:40Z, ~12 s before each reported stamp —
  consistent, not contradicted). Fresh **NEG-8 dual-family drift bound
  minted in-window**: gross single-member endpoint bound
  **0.750924420078 J**, replicated-endpoint (n=3) bound
  **0.570267900616 J** (verified in
  `runs_window_b_20260726_bound/neg8-drift-bound.json`, fields
  `single_member_endpoint_bound_j` and `replicated_endpoint_bound_j`;
  the lead's dictation called the latter the "triplet mean").
  **The whole-window verdict was still running when this entry was
  written and is recorded as PENDING. No result is asserted here.**
- **Window C** (`05_phase_decode_abba`): **two attempts, both failed on
  the clock slew**, both preserved in custody quarantine. Attempt 1 died
  at **ABBA member 7/40**; attempt 2 at the **dual-family bound mint**,
  which refused member `neg8-refcorpus-r11` (verified: that member's
  `metadata.json` carries `wall_minus_monotonic_span_s` =
  0.007769107818603516 s, and no `neg8-drift-bound.json` was produced in
  `runs_window_c_20260726_bound/`).
- **Window D**: **not started** (`runs_window_d_20260726*` are empty).

### Rough spend (estimates, not billing truth)

Four delegated calls carry figures: the Opus 5 contract lens ~164k
tokens / 50 tool uses / ~11 min; the Fable adjudication 21k tokens /
**zero tool uses** / 108 s; the Sol xhigh independent audit ~23 min and
the Sol xhigh clock diagnosis ~17 min (wall-clock only — per A-11 the
`codex-usage` feed remains unreliable, so no Sol token figures are
recorded). Lead orchestration, the bench catches, and all live
verification on top. Three additional `codex-run-v3` invocations failed
outright on the `WRITE_SCOPE` JSON defect (error 4) and a fourth did no
work under the read-only sandbox default (error 5).

### Verdict and calibration

- **The Opus-contract + Sol-execution pairing gained a second trial**,
  and each lens again found something the other structurally could not:
  the Opus lens traced a *whole labelled path* and found a
  cross-cell **attribution** defect mirrored into the validator (a
  contract-shaped catch, invisible to a probe that only asks "does this
  validate?"), while Sol produced a **runnable artifact-substitution
  probe** with concrete gate numbers (an execution-shaped catch,
  invisible to a reader tracing intended semantics). This is now two
  informal trials — **still not the pre-registered sealed A/B the
  project's own ≥2-trials protocol demands** (see ledger §6 A-8 and
  §5 Q1); the pairing remains the working default on argument, not on
  the project's own evidence standard.
- **Fable as adjudicator of a pre-assembled question is the session's
  strongest allocation datum**: 21k tokens, **zero tool uses**, 108
  seconds, and it **overturned the lead's own conclusion** about the
  lead's own failure, produced a better-shaped rule set than the lead
  had drafted, found failure modes the lead missed, and declined its own
  promotion. The generalizable shape is that the question had already
  been assembled — Fable did no retrieval, only judgment.
- **The auditor-adjudication pattern held again:** a fresh reviewer's
  blocker was correct-as-found and still correctly re-priced by the lead
  against the primary source. Sol's ignorance of L1 was a *feature*
  (independent rediscovery), and the lead reading `decision_log.md`
  rather than accepting the delivered severity is what converted it into
  the right record: **L1 stands, its blast radius is now recorded as
  wider, and it gained its first executable demonstration.**

### Dictated-fact verification notes

This entry was written from lead dictation and verified against primary
evidence. Two dictated line numbers were **off and are corrected above**:
the anchor-ceiling gate is at `joulewise/uncertainty_evidence.py:367`
(dictated `:366`, which is the offset-envelope computation), and the
unconditional `limited_without_admin` assignment is at
`joulewise/environment.py:908` inside `_probe_clock_sync` at l.904
(dictated `:904`). Two dictated facts could **not** be corroborated in
the surviving tree and are recorded as **lead-reported**: the
**5.544 ms** slew instance (no `wall_minus_monotonic_span_s` above
5 ms survives outside `neg8-refcorpus-r11`'s 7.769 ms, consistent with
attempt 1 having been quarantined out of `runs_window_c_20260726/`,
which now holds only its `instrument_validation` bundle), and the exact
window-B calibration stamps (see above). No window-C quarantine
directory was located under the repository root; only
`runs_window_a5_quarantine/` exists from an earlier arc, so the custody
location for the two window-C attempts is **not verified here**.

---

## C-039 addendum: the FIX-6..9 gauntlet, three cold gates, and the 7B floor window (2026-07-29/30)

Continuation of the C-039 index row above, covering the arc that carried
`impl/mint-tool` from `f63a334` to `969a4d6` plus mint #1 and the
`window_7bfloor_20260729` collection. Rulings from this arc are D-083..D-088 (D-088 in the same-day close-out);
the session ledger is the magistrate's own record. Topology: **magistrate**
(Fable, Ed's direct) adjudicating and operating the window solo,
**lieutenant** (Opus 5) directing the Sol pipelines and assembling packets,
**Sol** implementing and auditing, plus the rule-11 **cold gate** (fresh
Fable instance + Opus contract-lens refuter).

### Layers run

| Layer | Instances | Shape |
|---|---|---|
| Sol implementation (enforced `WRITE_SCOPE`) | 4 | FIX-6 `ea20a82`, FIX-7 `7f2c108`, FIX-8 `a14740d`, FIX-9 `969a4d6` |
| Independent audit / delta re-audit | 3+ | FIX-6 delta audit; FIX-8 audit; FIX-9+FIX-8 delta re-audit over `f188562^..969a4d6` |
| Cold gate (cold Fable + paired Opus contract-lens refuter) | 3 | F1 recorded in full (D-087); the pairing is the mechanism, not decoration |
| Magistrate bench verification | continuous | primary-text reads, bit-exact floor recomputation, QA-1 confirmation |
| Modularity survey (Explore agent) | 1 | produced the STACK-ID-BIND-01 lead |

### Unique catches, by layer

- **FIX-9 delta re-audit — blocker QA-1, the arc's decisive catch.**
  Overall verdict **FAIL** (Q1 FAIL, Q2 FAIL, Q3 PASS-WITH-CONCERN, Q4/Q5/Q6
  PASS). QA-1: *"a partial `physical_members` list can launder a
  within-member duplicate into one candidate."* A member declaring
  `bundle_ids: ["x", "x"]` with only one usable `physical_members` row for
  `x` yields a single candidate with identity `(manifest, member_index, -1)`;
  the one-row fast path then accepts its cooldown evidence **without ever
  invoking the supersession matcher**. The `-1` guard prevents a *valid*
  record from matching but does **not** guarantee refusal — a fail-open
  declared-occurrence laundering edge, and a violation of the magistrate's
  default ambiguity-refusal rule. **Magistrate bench-confirmed 2026-07-30.**
  This is the eleventh-plus datum for "fix rounds introduce defects": the
  ruled shape (D-086) was implemented correctly at the hop it named, and the
  defect lives at the *input-shape* boundary the ruling did not reach.
  Also QA-2 (should-fix): no repository fixture composes the real
  supersession validator/reader with the cooldown join — the FIX-9
  regressions stub the reader, which is adequate for join/matcher behavior
  and **insufficient as custody-path closure**.
- **FIX-9 delta re-audit — independent corroboration of the mint.** Q6
  verified the artifact is valid JSON, that its cell and transport-group
  values agree exactly, and that they round to the W6 pins **3.592138**,
  **7.377086**, **7.377086**, with the external statement carrying the same
  formula, roles, source, and no-double-count rule. Independent of the
  magistrate's own bit-exact recomputation (D-084).
- **Cold gate F1 — caught a defect in the magistrate's own packet.** The
  packet asserted `__init__.py` was in no granted `WRITE_SCOPE`; `f63a334`
  (FIX-5) had touched it and introduced the two-site surplus policy, making
  F1 the un-reverted half. The cold layer's value here was **against the
  magistrate**, which is precisely the disposition rule 11 exists to check.
- **Cold gate F1 — C2, the phase-order verification.** The cold instance
  verified from code that `_validate_output_separation` (`__init__.py:85`,
  called at `:1206`) runs **before** inputs load, so the filtered mapping
  does not exist at that point — converting "just filter it" into a
  design-bearing choice and forcing it up to the magistrate rather than
  leaving it to the implementer.
- **Paired Opus contract-lens refuter — narrowed the finding and supplied
  the adopted design.** F1 is **narrower than packeted** (refusal requires a
  surplus entry AND (symlink OR output-containment); no soundness exposure
  either way), and the refuter's **M3 — filter in place, preserve call
  order** beat the magistrate's own two-phase reorder proposal, which was
  **withdrawn**. M2's Opus-verified closed consumer list became a verified
  precondition. Second recorded instance this arc of a paired refuter
  out-designing the adjudicator.
- **Modularity survey (Explore agent) — STACK-ID-BIND-01.** Flagged that
  `analysis_engine/inputs.py:453` reads `artifact.get("sha256")` while
  `mlx_runtime.py:1064-1072` emits `folded_sha256` for directory
  (`file_set`) models — the only shape MLX produces — so
  `floor_stack_identity` returns `None` for real bundles while fixtures use
  the single-file shape and never catch it. CONFIRMED and fixed as FIX-7.
  A survey-shaped layer producing a real claim-side soundness defect.
- **Magistrate bench, B3 referral.** A Sol-vs-Opus **split** on the additive
  effective-clearable-effect reading was **synthesized from primary text, not
  majority-voted**, and resolved NOT-A-DEFECT with the Sol dissent preserved
  (D-083). B1 (device.boundary placeholders) was refuted; the referral
  question — whether the two citations address different objects — was
  answered YES from the clauses' own words.
- **Layer that produced nothing:** the B4 pending-refuter harvest closed
  **empty**. `ref/B4_sol.status` still read RUNNING from the pre-restart
  harness, `ref/B4_sol.md` was never written, and the background job had died
  with the old harness. Pre-assessed superseded / corroboration-only, so the
  disposition was unchanged — but it is recorded here as a **zero-catch
  layer instance** and as a second datum for the standing lesson that a
  background job which cannot wake its parent is a job that did not run.

### Window operation

`window_7bfloor_20260729` was operated by the magistrate **solo** (D-085):
quiet-lock covers all agent sessions, and a solo operator avoids the known
grandchild-notification misroute. Interaction was at stage boundaries only,
with zero tool calls during stages. The window completed **PASSED** and
claim-bearing on basis `3ff9128b…f1173`, through **two live contamination
events** (macOS's malware scanner, then a second, unidentified CPU
excursion — the operator log records only an hourly-snapshot *hypothesis*
for it) that the admission gates caught and that the protocol recovered from per its own written
playbook — the first arc in which the recovery path was exercised rather
than theorised. The **third-failure-closes** rule was ratified as cold-gate
precedent during this operation (D-087).

### Process observations

- **The escalation trigger armed and was honoured.** C3 armed the standing
  same-signature trigger before FIX-8 ran; the arc did not need to fire it
  for that signature. FIX-9 is a *different* defect at a different hop, not
  round three on the same one.
- **The cold-gate mechanism earned its cost this arc**: three exercises, one
  packet correction against the magistrate, one design substitution adopted
  over the magistrate's proposal, one code-verified precondition. Retain.
- **Open at the addendum's writing:** QA-1 is an unclosed blocker on
  `impl/mint-tool`; the merge train is gated on its disposition. QA-2, F2,
  F3, and Audit-F1 are registered in the 2026-07-30 queue intake batch.

### Addendum close-out (2026-07-30, later the same day)

The "open at the addendum's writing" state above resolved as follows. FIX-10
(Sol high, magistrate bench-reviewed, `16c7af0`) closed QA-1 with
declared-occurrence tallying and the real validator/reader/join fixture;
its own delta re-audit (Sol xhigh) then **FAILED with two successor
blockers** (QA-10A map-omission, QA-10B existing-retry laundering) — the
second consecutive same-signature fix-round failure. The standing escalation
trigger FIRED and was honoured: no FIX-11 was ordered; a mandatory cold gate
(fresh Fable + Opus contract-lens refuter, exercise #4 of the pairing) ruled
and the magistrate synthesized D-088 — join hardening moved to its own
gauntlet under a ratified contract; the branch merge licensed at the audited
head with the blockers registered.

Layer catches this round: the **delta re-audit layer** caught both successor
blockers a green 2280-test suite could not see (the fixtures were all
hardcoded `invoked`); the **refuter layer** caught that FIX-10 was conformant
with ruling R2 and the *ruling* was the QA-10B defect (a finding against the
magistrate, on the record in D-088 cl.6), plus the declaration-order
discriminator the cold instance's contract had missed; the **cold-gate
layer** caught the structural cause (the missing existing-outcome bit) that
both fix-round formulations had danced around, and the QA-10A escape path
through `floor_extraction`'s map-iteration completeness. Three independent
corpus scans (magistrate, cold instance, refuter) each verified both blocker
shapes absent from all claim-bearing evidence.

---

## C-039 addendum II: two escalation consults — the cooldown-join design consult and the contrast-window recovery (2026-07-30/31)

Second continuation of the C-039 index row. Both entries here are **consults
convened because an escalation trigger fired**, not council rounds convened by
ritual — one on a code defect class, one live inside a measurement window. The
rulings are D-089 (join) and the window's own §10 continuation record.

### (i) Cooldown-join design consult → D5-J (2026-07-30)

**Trigger.** The FIX-10 independent audit returned FAIL on B1 (coverage
checked against emissions rather than declarations, so a partial supersession
launders a declared-but-malformed occurrence) and B2 (filtered sibling
manifests never contribute declarations) — the **third consecutive round
leaving a residual of the same signature**. Per hard rule 11 the next spend was
a **design consult, not a fix round**; the merge train was held pending its
disposition.

**Layer:** Sol xhigh design consult, thread `019fb5c8…3937`,
codex-adjudicated with lead replays, question scoped to *where
declaration-completeness is enforced* (the ONE home).

**Unique catches:**

- **The consult reframed the defect class out of existence rather than
  patching its third instance.** D5-J moves the matcher contract
  observed→declared, which kills B1 *structurally*; catalog-completeness gate
  C answers B2 without a blanket directory-hygiene rule; the `-1` sentinel
  retires because declarations carry true positions. Three fix rounds had each
  patched a coverage site; the consult found there should be one owner.
- **A 23-cell truth table, of which the consult itself flagged one cell as a
  judgment call** — `(|D| ≥ 2, E ⊂ D, exact record naming all of D,
  selected ∈ E)` — and offered a collapse alternative rather than deciding it.
  The magistrate **STRUCK** the cell (uniform malformation ⇒ refuse;
  near-unreachable in any case; the cost of refusing is the standard
  repair-or-re-collect path), leaving **exactly two accepting shapes**. A
  consult that hands its adjudicator the one cell it should not decide alone
  is the behaviour the pre-decision-consult rule is buying.
- **Interim-merge answer NO.** The lead's own preference was a conservative
  interim guard (D1) that would license the merge now; the consult established
  D1 cannot cover B2, so the structural fix lands pre-merge. Second recorded
  instance this arc of the consulted layer beating the adjudicator's proposal.

Real-corpus behaviour is unchanged either way (**57/57, both supersessions
consumed**) — the blockers are adversarial-shaped and need corrupted custody
inputs. Implementation is FIX-11 in name, **structural in kind and
consult-sanctioned**, queued behind the metrology campaign authoring in the
same worktree. [RESOLVED 2026-07-31: implemented first (the authoring Sol
session had died), merged via PR #89 under the D-093 cold-gate synthesis;
metrology authoring relaunched after the merge on `impl/metrology-campaigns`.]

### (ii) Contrast-window recovery consult (2026-07-31, live in-window)

**Trigger.** Two consecutive same-signature failures of the start-triplet r1
slot on CPU admission (`cpu_busy_ratio_p95` 0.726 against a 0.5 gate), the
second after a relaunch premised on a **misattributed** cause — the operator
verified Time Machine was clear but did not verify overall CPU quiet, and the
true cause (an XProtect Remediator sweep) was still running. The standing
same-signature trigger fired; per rule 11 the next spend was a consult, not a
third blind relaunch.

**Layer:** bounded Sol xhigh consult, thread `019fb69a-7692`, convened by the
solo window operator between stages.

**Unique catches:**

- **The one-invocation supersession contract.** The consult established that
  the supersession recorder must be run **exactly once, post-window**, naming
  the selected occurrence and both superseded ones together. The operator's
  in-flight plan would have recorded per failure — **double-recording, which
  voids campaign membership downstream** (the recorder's silent
  duplicate-append defect, `SUPERSESSION-DUP-REFUSAL-01`). This is the catch
  that saved the window's claim-bearing status: the collection would have
  passed and the custody record would have been unusable.
- **The wait criterion: full sweep, not just the observed module.** The
  operator's instinct was to wait out `XProtectRemediatorPirrit`, the module
  actually observed at 941 CPU ms/s. The consult's criterion was the **entire
  remediator sweep** — modules run sequentially, so clearing one says nothing
  about the next. The sweep ran to 05:31Z; a second, unrelated intruder
  (`corespotlightd` at 624 CPU ms/s, Spotlight indexing the fresh bundles) was
  then also waited out, and round 3 launched only after a full-sweep
  completion, **eight consecutive daemon-quiet minutes past the Time Machine
  hour boundary**, and a clean final `powermetrics` tasks sample.
- **Continuation chain-shape verification.** The consult verified the round-3
  continuation was §10-shaped: it pins the window's original pre-calibration
  and re-runs the §5B screen, so the recovery does not silently re-baseline
  the window.

**Outcome:** round 3 ran the entire window **without a single further
admission event** — 40/40 science members usable, zero science-member
failures, whole-window verdict PASSED. The supersession was recorded once,
post-window, per the consult-verified contract. The window used 2 of its 3
permitted failures, both on one reference slot; the third-failure-closes
salvage rule (D-087) was never invoked.

**Process note.** This is the first recorded instance of the standing
escalation trigger firing **inside a measurement window** rather than over a
code defect, and of a consult being convened at a stage boundary by a solo
operator under quiet-lock. The cost was one consult against a ~2.6-hour window
that would otherwise have been re-run on a third guess; the mechanism should be
retained for window operation, not just for fix rounds.

## C-039 addendum III: the clock-anchor knife-edge consult (2026-08-01, in-window)

**Trigger.** Metrology window B's launch 1 aborted at the §5B
pre-calibration gate twice with the same signature
(`clock_anchor_unresolved` / `native_intersection_empty`) — and the
signature matched window A's post-cal attempt-1 failure from the prior
night. Three same-signature calibration failures across two windows is
exactly the standing escalation trigger's shape; per rule 11 the next
spend was a consult, not a third blind launch.

**Layer:** bounded Sol xhigh consult, read-only, one round, convened by
the solo window operator between launches (~01:00–01:30 PT). Full memo:
session scratchpad `693609a9…/scratchpad/consult_anchor_v2.md`; findings
ratified into D-099.

**Unique catches:**

- **The anchor is knife-edge by construction, and the lead's mechanism
  was wrong.** The operator's working theory was cadence drift in the
  capture stream. The consult showed the theory was
  quantization-confounded and replaced it: at 197 s capture length the
  native-second intersection margins were +0.86/+1.41 ms on the passing
  attempts vs −0.25/−0.26/−0.51 ms on the failures, while the
  *unmodeled* controller wall/monotonic rate (~−12 ppm ≈ 2.3 ms per
  capture) exceeds every margin — pass/fail at this capture length is
  quantization-phase luck, an instrument-design finding (rate-aware
  anchor mapping is the queued repair) rather than an environmental
  fault to wait out.
- **Time Machine exonerated, and the prep-script proxy with it.**
  `tmutil destinationinfo` showed no destinations configured; the prep
  script's "TM RUNNING" line detects process residency only. This
  retroactively taints window A's failure-#3 "TM-consistent"
  attribution and re-identifies the overnight intruder class as
  mobileassetd/softwareupdated (~04:29 PT both nights) plus bird.
- **Discipline on the causal claim.** The consult recorded bird (99%
  CPU uploading the prior window's 10.4 GB backup) as *plausible
  trigger and objective preflight violation* — explicitly NOT confirmed
  root cause. The distinction is what kept the relaunch decision
  honest: launch 2 proceeded under a hardened protocol (bird-SIGSTOP
  with identity custody and a fail-safe CONT trap) plus a predeclared
  budget (frozen chain unchanged, built-in retry pair only, night
  closes if the gate aborts again), rather than on a claimed fix.

**Outcome:** launch 2 passed pre-calibration on the first attempt
(b_fiducial 0.032787 s) and the window collected its core payload
through to a clean salvage close. The consult cost one bounded session
against an 11-hour runway that two more blind aborts would have burned.

**Process note.** Second recorded instance of the escalation trigger
firing inside a measurement window (first: C-039 addendum II (ii)), and
the first where the consult *refuted the lead's mechanism* while
confirming the lead's decision shape. The pattern holding across both:
the consult's unique value is causal discipline under time pressure —
separating "what we can prove" from "what we are tempted to conclude"
before the next launch is committed.
## C-040: The commit-3 gauntlet — five fix rounds, two cold gates, and what each layer uniquely caught (2026-08-01/02)

**Shape.** Composed commit (Sol xhigh, ratified design) → independent
delta audit → fix rounds each followed by a FRESH-thread re-audit →
rule-11 cold gates when triggers fired (twice) → [outcome line filled at
close]. All delegated; magistrate gates: suite + mapping-hash pins at
every head, bench verification of every load-bearing audit claim before
acting.

**Per-layer unique catches (zero dead layers this arc):**
- Implementer self-verification: caught nothing the auditors later
  confirmed as remaining — necessary but NEVER sufficient, again.
- Audit 1: crash-strand ordering, v1-pinned verdict verifier (a DESIGN
  scope omission it attributed as implementation), path normalization.
- Re-audit 1 (fresh): proved fix-1's heal unreachable-shaped and the
  same-signature persistence that fired the trigger.
- COLD GATE 1 — cold instance: THE ROOT CAUSE (the design's
  attest-after-publish clause guarantees the crash window; both prior
  rounds were downstream patches). Refuter: the design's TWO
  contradictory acceptance clauses; the pointwise-vs-enumerative
  aggregation distinction that OVERTURNED the cold instance's B2 order
  (magistrate overruled with dissent, bench-verified); the torn-log-line
  second brick + its v1-history regression that the re-audit had called
  acceptable; the B2 trigger miscount (round 1 had no license).
- Re-audit 2: three narrow adjacencies in an otherwise-passing
  structural implementation (fail-open lock surfaces, tolerance
  breadth, test fidelity).
- Re-audit 3: unbound lock token; enumeration-shaped tail (the pattern
  recurrence that fired the second gate).
- COLD GATE 2 (convergent): both instances independently probed
  CPython's json taxonomy and rejected BOTH magistrate candidates.
  Refuter uniquely: the whitespace-preservation hole (json.loads
  tolerates trailing whitespace → permanent acceptance of
  writer-impossible bytes) that had survived FOUR prior reviews; the
  packet's miscited B3/NUL precedent. Cold instance uniquely: the
  '{"a": 1e' false-refusal proving pos-based refinements unsound; the
  byte-exact canonical round-trip construction.
- Re-audit 4: token aliasing across release/reacquire (bare-Path
  registry keys); two recognizer grammar corners (canonical key
  ordering; -0.0); single-fd TOCTOU; exception-path cleanup.

**Process findings for the skills:**
1. Fix rounds introduce defects — now proven FIVE consecutive times on
   one commit; the fresh-thread re-audit after EVERY round is
   non-negotiable doctrine, permanently.
2. The refuter layer's value concentrates exactly where instances agree
   too readily: both its overturning arguments (B2 aggregation; the
   whitespace hole) came with runnable probes, not rhetoric. Keep
   requiring probes in refuter briefs.
3. Formulation-vs-implementation trigger parsing is a loophole risk:
   the D-104 disposition note's pattern (one explicit fidelity round,
   then ANY blocker → gate + descope, no further parsing) is the
   containment shape to reuse.
4. Directing-subagent stalls (4×) and the MCP 1800 s timeout: audited
   CLI route for >30 min Sol rounds; harvest-from-disk + process
   watchdogs as standing practice (memory recorded).
5. Magistrate candidate formulations in cold-gate packets get REJECTED
   when drafted at the bench under fatigue (both round-4 candidates) —
   the gate caught both; drafting candidates is still net-positive
   (they focus the ruling) but they must be labelled candidates, never
   presumptive.

**COLD GATE 3 (disposition, 2026-08-02) addendum:**
- Round 5 closed the lock mechanism entirely (all identity attacks
  incl. field-copied clones) but left two recognizer-exactness
  blockers; the binding commitment fired as written — no round 6.
- Cold instance: Option A on the merits with verbatim fences + complete
  closure procedures; its own wider absence scan (40 files vs the
  packet's 33 — depth-1 glob error caught); demanded the third
  independent scan and made lead live verification an explicit merge
  condition rather than trusting the packet's uncited green claim.
- Refuter (the arc's strongest document): did NOT oppose landing;
  replaced the fences — the preserve-then-truncate custody sidecar
  (classifier errors can no longer destroy evidence, decoupling
  exactness from custody), the 2-line writer-side ASCII key assertion
  (closed five unvalidated splice sites nobody had seen), proof the
  ratified R7 pin was implemented over a synthetic corpus and missed
  F1 by ONE character position, proof the number-grammar's literal
  subset direction is undecidable-at-sane-cost (three rounds failed on
  it), the branch-introduced-vs-pre-existing precedent distinction,
  and the packet-hygiene finding (runway/cost-of-delay context reached
  a cold instance — recorded as a process rule: sealed annex only).
- Synthesis D-105: land via custody micro-commit + narrow audit;
  registration as a NEW ruling; exactness struck for a documented
  decidable superset; D-104 cl.2 amended.
- Layer scorecard update: the refuter layer has now overturned or
  materially amended the magistrate/cold-instance position at ALL THREE
  gates — it is the single highest-unique-catch layer of the project
  and its probe-required brief format is ratified practice.

**Outcome.** Gauntlet commit 3 MERGED as PR #93 (`cb860e1`, 2026-08-02):
composed commit + five audited fix rounds + custody micro-commit +
bench fixes + the frozen exact-set pin; suite 2352 OK at the final
head; 57/57 + 47/47 mapping pins hash-identical at every head of the
branch; COOLDOWN-JOIN-GAUNTLET-01 and QA-10A/QA-10B retired; the D-088
standing conditions and D-093 scans lifted per their row contracts;
residual exactness blockers registered non-downgradable in
C3-RECOGNIZER-EXACT-01 under D-105's compensating controls (custody
sidecar; writer-side key assertion). Total spend: ~6 Sol implementation
sessions, 6 independent audits, 3 cold-gate pairs, across ~20 hours of
the Ed-authorized runway — the most heavily reviewed change in the
project's history, protecting the machinery every future claim
consumes.

## C-040 addendum: the b-ii cold gate (D-106), the merge-fallback landings, and the codex envelope bug (2026-08-02/03)

**Shape.** The runway's second half ran both repair branches through
brief-repair rounds to decisive re-audits: MANIFEST-CONTRAST v3 came
back CLEAN (zero findings) and merged as PR #95; MET-DANGLER's decisive
re-audit left ONE blocker (B3-R1), the disposition note's binding
commitment fired as written — no third formulation round — and the
question went to the runway's FOURTH cold gate (cold Fable + Opus
contract refuter), synthesized as **D-106 Variant D**. Full packet and
re-audit custody: `.desk/coldgate_d100_bii/`.

**Per-layer unique catches (no dead layers):**
- Decisive re-audit (Sol xhigh, fresh thread): B3-R1 itself — after two
  formulation rounds, telemetry and nested content remained unbound to
  the admission-only event account (earlier-capture substitution
  licensed; negative time deltas accepted; nested `model_output`
  unrecognized-and-passing). Also re-proved all five regressions red on
  the parent by code inspection, under a code-inspection-only ruling.
- Cold instance: Option A + window-B YES on the compensating-control
  theory; its own stated strongest counterargument (doctrinal fences
  decay) converged with the refuter's B-1 — recorded as dissent when
  overruled.
- Refuter (Opus, contract lens): the gate's decisive layer for the
  FOURTH consecutive time, all showings bench-verified — the recorded
  manual verification contains ZERO bundle digests, so Option A's fence
  binds by path against a content-substitution defect; the packet's
  condition-3 parenthetical quoted only the half supporting the
  magistrate's lean; the window's three sibling quarantine bundles are
  mutually substitutable by one same-name copy, defeating the
  rider-(ii) exemption; the NEW writer-level fact (powermetrics emits
  identity-free 8-field rows from one code path, so per-file schema
  formulations can NEVER bind capture identity) that diagnosed both
  failed formulations and discriminated the fix in kind; and S-1 — the
  D-105 registration guard inverted on first contact (it registered
  the undecidable; this residual is decidable), so NOTHING is
  registered.
- Magistrate: Variant D synthesis; two packet-hygiene failures recorded
  against itself (the Option C runway line; the selective quotation);
  cold-gate packet authorship moved to MECHANICAL assembly permanently.

**The merge-fallback pattern (twice, ruled):** GitHub could not build or
schedule merge-ref CI for PR #94 (pull_request runs never scheduled;
close/reopen tried) or PR #95. Ruled fallback, both times: satisfy
D-072's substance far past precedent (three independent audits + cold
gate + lead full suite at the audited head + hash-identical mapping
pins; for #95, the composed-tree full suite as the lead integration
gate), merge, and treat the push-to-main verdict CI as the verdict with
immediate revert on red. Both verdict runs came back green.

**Site failure domain (D-101 addenda I+II):** the D-106 decision-log
commit itself turned main red through the live-content site pack tests
— a governed record edit acting as a session blocker, which D-101
forbids in substance. The defect was fixed on its merits (anchor
minting), the CLASS closed by Ed's directive (live-content site tests
advisory-lane, addendum I), and the site observatory then split into
its own workflow and failure domain (addendum II; separate `site`
workflow 2/2 green).

**Process finding — the codex envelope bug:** both of the runway's
final xhigh runs (the D100-BII implementation; the TEST-SPEED consult)
completed their work but lost the final envelope — protocol failure by
contract, so the implementation diff was HELD untrusted on its pushed
branch. Root cause (found 2026-08-03): a codex CLI models-cache schema
drift — cached entries lacked `supports_reasoning_summaries` and the
TTL-renewal deserialization killed sessions before the final message.
FIXED 2026-08-02 evening (stale cache moved aside, fresh refetch
carries the field, trivial Sol run verified end-to-end). The
held-untrusted → independent-focused-audit disposition worked exactly
as the bridge contract intends: no envelope, no trust, regardless of
how green the work looked.

**Outcome.** PRs #94 and #95 MERGED at audited heads with green verdict
runs; D100-BII-BINDING-01 minted (P1) carrying D-106 clause 3's four
parts; window B re-evaluation hard-blocked on it; its focused
independent audit launched 2026-08-02 evening (successor session) with
the repaired codex path. Layer scorecard: the probe-required refuter
brief format remains the project's highest-unique-catch instrument —
four gates, four material amendments or overrulings.

## C-041: The D100-BII nested-closure arc — two more cold gates, a third-failure STOP, and the CAL-BRACKET consult (2026-08-03, desk session in Ed's absence)

**Shape.** One desk session ran the two open repair branches
(D100-BII-BINDING-01, CAL-BRACKET-D079-01) and the MINT-GENERALIZE
tooling to their conclusions, plus two cold gates on the b-ii
nested-content closure. All delegated; magistrate gates: lead full-suite
+ live bench probes at every disposition. Roles: Fable magistrate;
Sol xhigh execution/audit/consult; cold Fable instances + Opus refuter
at the gates.

**D100-BII arc — three formulations, two gates, STOP (full detail:
`.desk/coldgate_d100_bii/`).** The nested-content closure (D-106 clause
3(c)) failed three structural formulations:
- Formulation 1 (position-enumeration) + formulation 2 (key-denylist):
  cold GATE 2 → **D-107**, adopting the refuter's C-A′ producer-derived
  admission grammar with per-leaf value domains; scope expanded to the
  inventory grammar + the 769/769 false-refusal repairs; row acceptance
  amended with an over-refusal gate (license 3/3 real subjects). The
  refuter's fifth consecutive material amendment: it proved the license
  tool refused all three real subjects at the inventory gate at every
  head, that fix-1 over-refused 769/769, and that four value channels
  stayed open.
- Formulation 3 (open-superset leaves): fix-2 implemented C-A′ but left
  free-text `node_cleanup.error/.path`, the argv superset, and numeric
  leaves open — bench-confirmed workload text licenses. Cold GATE 3 (two
  cold Fable instances converged on L-A surface-refusal; Opus refuter
  DECISIVE): the refuter proved (a) the packet censused the wrong
  population (telemetry.command 0/26 on the license surface, and L-A's
  natural implementation false-refuses 772/772 via a second .command[]
  path), (b) four MORE open carriers, (c) **structurally**, the grammar
  constrains values but not list CARDINALITIES — an unbounded list over
  a closed alphabet is an unbounded workload channel (fires D-107 clause
  7's second return trigger), (d) ~1.2 KB of free numeric-leaf capacity
  remains under any grammar, the same order as the workload output, so
  clause (c) **cannot achieve D-100's "zero output bytes" predicate by
  any bench formulation**, and (e) the substitution attack (c) was
  ordered to close is **already closed by the landed clause (b)**
  hash-sealed manifest pin — so (c)'s real residual is against a careless
  closure author, not substitution.
- **Magistrate disposition: STOP the bench loop, escalate to Ed
  (D-108 pending).** Not a fourth round — three formulations + a
  structural-impossibility finding + a proposal to retire a ratified
  clause is exactly the sunk-cost pattern rule 11 exists to halt.
  Nothing committed; fix-2 diff held untrusted; window B stays blocked.

**Per-layer scorecard (this arc):** the Opus refuter layer amended or
overturned the disposition at BOTH gates (2 and 3) — now the sole
highest-unique-catch layer across SIX consecutive gates. Cold Fable
instances: converged correctly on shape both times, but neither reached
the structural cardinality/capacity finding — the cross-model pairing
earned its keep again (a fresh Fable shares the magistrate's own
dispositions). Packet hygiene: the refuter recorded FOUR findings against
the magistrate's gate-3 packet (selective clause-7 quotation omitting the
half that decided the gate; flags not quoted in full incl. the blocking
anti-round-3 disposition; a laundered "769/769 admit" number; wrong-
population census) — the same classes recorded at D-106/D-107. Standing
correction adopted (recorded in the gate-3 synthesis): quote governing
clauses to the period, quote every source flag in full including the ones
cutting against the proposed disposition, census the license-surface
population.

**CAL-BRACKET arc — consult over blind round three.** Impl + fix-round-1
(first-audit blockers cleanly closed) → delta re-audit FAIL, 3 freshness
blockers, estimator-digest a REPEAT signature. Per the escalation trigger
the next spend was a read-only Sol xhigh DESIGN CONSULT, not a fix round.
It resolved each against D-102: F1 (freshness=6-field epoch) determined;
F2 (4-module estimator digest set) magistrate-ratified from the
b_fiducial_s dependency graph; **F3 (cross-root trigger observability)
escalated to Ed (D-109 pending)** — D-102 mandates the triggers but no
authoritative universe/registry exists; build one vs. narrow D-102 is a
claim-soundness call. Held for a single combined fix round after Ed rules
F3 (it controls the artifact schema). Detail: `.desk/calbracket_d079/`.

**MINT-GENERALIZE-01 — landed.** Full gauntlet (impl → audit → fix →
delta clean → bench fix → lead gates → PR #96 green CI) merged under
D-072; live 7B mint stays lead-reserved. The clean case of the session.

**Process finding for the skills.** Two claim-machinery closures this
session hit genuine DECISION-LEVEL gaps (a clause that cannot meet its
predicate; a mandated trigger with no defined mechanism) that the
adversarial bench correctly SURFACED rather than papered over. The
system worked precisely because the escalation triggers were honored
(consult-not-round-three on CAL-BRACKET; STOP-not-round-four on D100-BII)
— the opposite of the 2026-07-26/27 failures that motivated rule 11.
Recorded as evidence that the topology holds when the loop-immersed agent
actually chooses to stop.

## C-042: Ed-requested pre-ruling debate — 2 Sol xhigh rounds over the D-108/D-109 packets, both packets materially changed (2026-08-03)

Shape: bounded 2-round adversarial consult (MCP discussion lane,
read-only, thread `019fc9bb-73fd-7042-8faf-2a72d74ee5b3`), Sol
instructed to bench-verify packet claims rather than trust them, given
the magistrate's recorded selective-quotation history. Ed then ruled by
explicit deferral to the joint position → D-108 + D-109. Full record:
`docs/process_traces/2026-08-03-d111-backfill/debate-d108-d109/` (tracked).

Unique catches, by layer:
- **Sol round 1 (packet audit):** (1) the D-108 packet's "three
  subjects manually verified" overstated the durable record — full
  b-ii facts exist for the two r08 attempts only; (2) the packet's
  A-min formulation was UNSOUND as stated — writer crash-window
  (capture state created pre-receipt, pre-manifest failure exits)
  defeats publish-on-return receipts, and baseline-prefix ⊆ current is
  not anti-rollback; (3) L-A′ "verified" was a summarized result, not
  a banked executable artifact. All three lead-verified at the bench
  and adopted (reservation-first + independent head pin now R1 law).
- **Sol round 2 (code refutation):** the magistrate's two-subject
  license-surface counter was WRONG — the closure loader requires
  exactly three D-087 occurrences and inspects every one; evidence
  surface ≠ exclusion target. Adopted into D-108 clause 2.
- **Magistrate (context the peer lacked):** schedule pressure LOW
  (recorded), metrology-centric pivot (instrument is the product), and
  shared-R2 marginal-cost analysis — flipped Sol's B recommendation to
  A-min-with-reservation, withdrawn on the record.
- **Convergence quality:** two Sol catches survived verification, one
  magistrate counter died to code, one Sol recommendation flipped on
  supplied context. Both directions of the bridge earned their spend;
  the consult-before-ruling shape (rule 2 amended default) validated
  again on a decision-level packet.

Residual Sol dissents preserved in D-108/D-109 text: three-occurrence
evidence surface; 32/6 dispositions need raw-physics backfill before
issuance; A-min threat-model honesty clause.

## C-046: Retrospective — CAL-REBRACKET-01 max-bracket consumption gauntlet (2026-07-26)

**Retrospective record, authored 2026-08-03 for CRB-6.** This entry
reconstructs the missing council row from the completed `CAL-REBRACKET-01`
table record in `TASK_QUEUE.md` and the durable 2026-07-26 session record at
`docs/process_traces/RESUME-2026-07-26.md`; it does not invent a
contemporaneous transcript.

Shape: two parallel independent design consults rejected persisted derived
summaries and converged on D2+ — authenticated re-derivation at consumption
time under `max(B_pre, B_post)`. Three implementation rounds and three
independent adversarial audits then converged clean. Outcome: PR #86 merged as
`7b12f20`; replayed a9 (7 members) and a10 (37 members) both passed
consumption with every member widened and point estimates unchanged. The lead
gate recorded 2164 passed / 21 skipped at the rebased head, with all five CI
checks green.

## C-047: The 16h runway — two gauntlets, the winB STOP gate, the concurrent-sweep interception (2026-08-03)

Full record: `docs/run_reports/2026-08-03-16h-runway.md` (the ONE
home); decisions D-108..D-112. Shape: Ed-granted autonomous runway with
joint Fable+Sol decision authority; a PARALLEL Fable instance delivered
the two-week soundness sweep mid-runway (Ed-initiated concurrent-audit
pattern — validated, memorized, D080-TRIGGER-01 queued).

Unique catches by layer: Sol audits — D-108 F1 (retirement
over-drop), D-109 B1/B2 + four weak fences; Opus contract refuter —
expired NEG-8 bound, cascade-spelling falsification, F7 barred-cell
scope question, falsify-by-removal sole-cause proof; cold Fable —
stage-1-clean control-flow proof, spelling-collision (two producers),
masking-latency explanation; concurrent sweep — RT-1 (intercepted the
in-flight 7B-mint license neither in-session consultant could see);
lead bench — two fix commits, clause-(d) re-record, byte-identical
pinned replay, exit-status-masking recurrence self-caught. Fix rounds
introduced defects twice more (data #11, #12). Both gauntlets held;
the deviation escape and rule-11 gates fired as designed; the night's
one claim-surface outcome is HONEST SHRINKAGE (CLAIMS_STATUS §1 =
NONE under D-110) plus a proven-honest toolchain (byte-identical
replay).

## C-048: Integration-collision resolution — consult-shaped amendment, delta re-audit catches a live guard bypass (2026-08-04)

Session: successor magistrate, T3-drive era; the first decision handed
off by C-047's close. Full record:
`docs/process_traces/2026-08-04-calbracket-integration-collision/`
(FINDING + RESOLUTION + both Sol reports) and the consult directory
beside it; policy: D-109 addendum II.

Shape: bounded pre-decision Sol HIGH consult (rule 2 amended; Ed's
effort cap held — no xhigh anywhere this arc) → Sol HIGH enforced-scope
implementation → lead bench diff-read + full-suite replay ON THE
INTEGRATION TREE (2487 OK, exit-0 unpiped) → fresh Sol HIGH delta
re-audit → bench hardening from the auditor's specified fix shape →
merge-ref CI green. Merge itself: harness classifier denies agent
`gh pr merge`; Ed names merges (standing pattern, reconfirmed).

Unique catches by layer: PRE-DECISION CONSULT — the byte-identity
oracle correction (historical-digest replay would have CONTRADICTED
D-110; integration-tree core-vs-wrapper parity adopted instead), the
review-pinned rename, the snapshot-identity regression spec. DELTA
RE-AUDIT — the repr-'None' default spoof PROVEN LIVE against the
rendered-signature pin (guard passed while the core's is-None load
path was defeated), plus the remerge-tree fidelity proof and the
loader-mutation kill of the new regression. LEAD BENCH — the piped
exit-status recurrence self-caught AGAIN (third occurrence; the unpiped
re-run is now reflex, the habit clearly is not), stale RUN_STATE
claims (char captures "collected" that never ran; F1's byte-frozen
framing in active restart text). CI — remains the only layer that
structurally sees the merge ref before merge.

Instrumentation note: two HIGH-effort Sol instruments again produced
blocker-grade unique catches (consult F1, audit F2) — Ed's cap shows
no quality decline through this arc. The delta-re-audit rule (every
fix round) paid for itself on a 127-line mostly-test amendment.

## C-049: The 12h autonomous marathon — issuance through the gate, six PRs, and the fork the first consumption exposed (2026-08-05/06)

Session: Fable magistrate, Ed's 12-hour autonomous window (directive
batch 2026-08-05 ~22:00: effort cap lifted, fast tier specified,
D-113 ruled (c), overnight issuance pre-authorized conditional on the
gate). Full records: `docs/process_traces/2026-08-06-d079-issuance-coldgate/`,
`docs/process_traces/2026-08-06-d110-remint-fork/` (DIAGNOSIS, consult
prompt+response, SYNTHESIS), RUN_STATE checkpoint blocks of 2026-08-06
(morning + afternoon + late), plus the per-arc consult traces of
2026-08-05 in `docs/process_traces/`. This entry is the owed council
record assembled by the 2026-08-07 successor from those artifacts.

Shape, in sequence: (i) four checkpoint audits harvested → D-115
adjudicated (Q2 fixed installation capability w/ binding conditions);
(ii) two rule-11 escalation consults after same-signature counters hit
2 — CGV F3 absolute-path-bypass (consult-adopted restructure replacing
the denylist approach) and QG census observation→absence class (Option
C redesign, magistrate stop-condition set); (iii) fix rounds each
followed by xhigh delta re-audits; (iv) the D-079 issuance rule-11 cold
gate — SPLIT verdict, fresh-Fable PROCEED vs Sol-xhigh contract-lens
HOLD — magistrate UPHELD the HOLD; (v) issuance reframed from "an edit"
to a design-bearing consumer implementation, run through the full
gauntlet (PR #108 consumer, PR #109 execution + ledger genesis import +
5-file test reconciliation; two cold gates, adversarial audit + 3 delta
rounds, exact-bytes dual cold review); (vi) D-116 issued, PR #109
merged on green under D-072 at gate-reviewed head `d85b4f9`; (vii) the
FIRST consumption attempt against the issued regime → structural
finding → Sol xhigh pre-decision fork consult (run
`20260806T165843Z-10884`) → magistrate synthesis.

### Unique catches, by layer

- **Rule-11 cold gate (the flagship):** the issuance HOLD caught that
  the packet was underscoped — F1: `calibration_bracketing.py` had NO
  consumer path for an issued acceptance artifact (a JSON flip would
  have made it unloadable in production); F2: `derivation_sha256`
  covers the whole artifact core, so the assumed "n=19 preserved ⇒
  digest preserved" was FALSE (lead-reproduced). An irreversible ledger
  write paired with a production-refused artifact was prevented. The
  split verdict was synthesized by the magistrate (rule 9), not
  majority-voted.
- **xhigh delta re-audits (fix rounds introduce defects — proven
  again, twice):** QG F1 — idempotent init retry reporting success with
  unresolved directory-fsync durability (introduced by fix round 1);
  CGV B1 — malformed digest arg serialized verbatim into REFUSE
  receipts (live-proved) and B2 — a non-CommonMark phantom fence hiding
  real duplicate headings from the pin check.
- **Oversight/prune lens (cgv-audit-B):** PASS receipt did not bind the
  judge to the validated bytes (post-validation exhibit substitution),
  plus the prune recommendation that reframed F3's whole subsystem —
  the finding that triggered the CGV consult.
- **The consumption attempt itself as a layer:** only the live attempt
  exposed that import-marked receipts are excluded from candidate
  discovery BY DESIGN (CAL-BRACKET arc, retained through issuance), so
  no historical window can pass authenticated max-bracket consumption
  at main — every refusal fail-closed; campaign logs sha-verified
  untouched. Desk review had not predicted it.
- **Fork consult (Sol xhigh):** verified all five historical bracket
  pairs physically exist under the drift screen (the objection is
  provenance completeness, not causality); recommended Option 2 (three
  compact prospective windows) over finite-allowlist historical
  candidacy (Option 1, preserved cold-gated); flagged the D-113
  dependency rewire; supplied the unblocked-regardless desk queue.

### Dispositions and open state at close

D-113 transcribed (`8e68cde`); D-115 on main (`0941cf5`); D-116 on PR
#109; PR #109 merged (`c537386`). Magistrate + consult CONCUR on
Option 2; **Ed had NOT ruled at the machine-move stop** — his ruling,
the prefill-contrast shape ack, and three-nights scheduling were the
owed items handed to the successor (RUN_STATE checkpoint block).
Wrapper gotcha re-recorded: codex-run-v3 takes the prompt as a literal
string, never a file path (one consult killed + relaunched cleanly).

## C-050: The paper-first session — the MVP draft shipped, 24 directions adjudicated, and the paired-audit layer's biggest day (2026-08-07)

Session: Fable magistrate, Opus 5 lieutenant lanes, Sol as workhorse.
Ed's directives, in order received: resume from checkpoint; **abandon
the t3 work — MVP capstone paper first, the rest later**; a 14-hour
autonomous window and the 3-quiet-nights-plus-desk-work path (which
became **D-117**); a **Sol burn** (3 h unlimited, extended to 12 h) with
fast mode everywhere and ~20 paper investigations run far ahead of the
council; **Opus 5 counter-reviewers** on every paper idea; and
plan/spec/implementation drafting staged for later review (Opus
examines Sol drafts, Sol adjudicates, Fable reviews last). Full records:
`docs/run_reports/2026-08-07-paper-first-session.md`;
`docs/process_traces/2026-08-07-{d117-plan-freeze,night-hardening,d117-u-units,meta-sweeps,plan-factory,prefill-feasibility}/`;
`docs/strategy/2026-08-07-paper-portfolio/` (24 proposals, 24 reviews,
two syntheses, ADJUDICATION); paper records
`docs/paper/draft-v1-review-round2-lens{A,B}.md` and
`docs/paper/bibliography-audit-2026-08-07.md`.

Shape, in sequence: (i) the **paper gauntlet** — two review lenses
(metrology-fidelity; plain-language/coherence, both returning REVISE) →
a web-verified **bibliography and novelty audit** → a **Sol xhigh fix
round** of 14 items → **delta re-audit** → **bench fidelity corrections
read against the CODE** → PR #110 merged (`6a70707`); (ii) **D-117**
transcribed from Ed's ruling (D-110's historical re-mint order
superseded; three prospective windows), with CLAIMS_STATUS un-staled;
(iii) the **plan-freeze design consult** — Sol xhigh design memo
ratified (gates 1-8 adopted, work orders U1-U10, identifier scheme,
two-stage pin freeze, zero calibration retries, U2 cold-gated);
(iv) a **night-hardening 3-lens sweep** over the runner, calibration/
ledger, and extraction/mint paths, plus a separately-charged paper-vs-
code fidelity audit; (v) the **paper-portfolio factory** — 24
directions (20 directed + 4 open-ended) developed by Sol high/fast,
each adversarially counter-reviewed by an Opus 5 referee, then two
**opposing-prior** Sol xhigh syntheses, then magistrate ADJUDICATION;
(vi) the **U1 and U3 implementation units**, each through paired
contract+execution audits and a lead-dictated fix round (U1: 8 items,
then an xhigh delta; U3: 7 items, delta owed); (vii) read-only
**meta-sweeps** (refusal census, contamination desk study, decision-log
coherence, queue staleness, council-log layer yields, skill drift, pack
scout, production-format scout, docs-vs-practice); (viii) a **plan
factory** of 8 far-ahead Sol drafts, explicitly staged for council
review rather than landing.

### Unique catches, by layer

- **Paired audit lenses (contract + execution) — the session's
  highest-yield layer by a wide margin.** U3 CONTRACT live-proved that
  postcollection custody and D-110 allowance pins are **self-attested,
  not authenticated**: every receipt/content/binding/head/report hash
  replaced with fabricated values and `observed_drift_s` /
  `applied_allowance_s` tampered to `0.000001`/`0.010818`, the pinset's
  own self-hashes repaired — and the four-cell artifact **still
  minted** (CRITICAL); the same lens found the mint **deriving its own
  six-decimal literals** (HIGH), the exact behaviour D-084's
  never-derived requirement and the design memo prohibit. U1 CONTRACT
  found L5 not closed — intended-window identity and `runs_root`
  binding were **optional** — and that aborting a session **deletes
  finalized observations from D-109's authoritative trigger universe**
  (both BLOCKER). U1 EXECUTION live-proved **concurrent double-arm
  acceptance** (two synchronized writers both `accepted` into the same
  reserved slot, one ledger line) and **open-session candidate
  leakage**, and showed that the test named `never_leak_as_candidates`
  **asserts the leak** it purports to forbid.
- **Delta re-audit (fix rounds introduce defects — the record holds).**
  U1's fix round closed 7 of 8 items and preserved the D-116
  issued-prefix replay byte-identical, but the delta found an
  **INTRODUCED blocker at the recovery boundary**: an interruption
  after recovery evidence is written but before journal clearing leaves
  the next recovery computing different evidence counters and refusing
  governed closure. FIX-6 stands PARTIAL; the torn-tail class is the
  only one whose signature survives, so FIX-6b carries a binding
  no-round-three stop-condition (next recurrence is a rule-11 consult).
- **Opus referee corps (24 counter-reviews).** A **systematic sizing
  error across the portfolio** — proposals sized against the generic
  ~5 J bar when their 7B arms face the measured **~14.0 J armwise
  floor** (comparative 13.998036715259254 J, the only actually-minted
  comparative floor); flagged independently in the cross-runtime,
  MoE-routing, MTP, parameter-scaling, KV-context and prefill reviews,
  several of whose kill gates sat *below* the floor they had to clear.
  The **Window-C/§6 evidence gap**: draft §6's six characterization
  rows — contribution C-iv — are all `[PENDING WINDOW C]`, D-117 funds
  no Window C, and D-117 cl.4 places the broader campaign *after* the
  three-window closure, so one of the paper's advertised contributions
  would ship with zero evidence, with no decision entry recording that
  choice. The **anti-conservative floor transport** rule in the
  prefill-scaling design (repeatability scales with magnitude; floors
  do not transport across workload lengths). And the **missing
  advisor-lineage citations** — the referee on the advisor-lens
  proposal caught that `draft-v1.md` §8 cited RAPL-in-Action, Jay &
  Ostapenco, MLPerf Power and SPEC and **neither JouleSort nor
  Mantis**, i.e. the paper did not cite its own advisor's foundational
  work, and that the one session tasked with the advisor's perspective
  had missed it.
- **Bibliography and novelty audit (web-verified).** All **13/13
  citation keys resolve to real, correctly identified works**; the §2
  three-leg novelty claim **STANDS** (no published `powermetrics`
  validation study of any kind exists through 2026-08); 12/13
  characterizations accurate, with **one factual error** — F-BIB-1, the
  draft attributed load/baseline/transfer dependence to the
  disaggregation paper's ENERGY outcome when the paper conditions its
  PERFORMANCE benefits and reports energy essentially unconditionally
  higher — corrected in §8 the same round. Eight pre-submission
  double-checks queued.
- **Meta-sweeps (read-only, Sol high/fast).** The **refusal census**
  quantified §5's refusal-log claim and evidenced the pre-window
  plumbing item: of 44 refused member occurrences only 14 have a
  reconstructable causal reason (**30 have none**), and at the
  member-identity level the reconstructable rate is **34.2%** (13 of 38
  identities) — two different denominators, both reported, neither
  derived from the other. The **contamination desk study** swept **742**
  historical idle captures and found member-length burst excess above
  1 J in **35.0%** of 93 s windows and 31.9% of 97 s windows, **never
  above 5 J**, worst observed 3.21 J — with the honesty caveat the
  study itself insists on: only **two** ~360 s app-resident
  characterization captures were long enough to host member-length
  windows, the ~4,400 placements per width are heavily overlapping and
  strongly dependent, and the rates are NON-CLAIM/DIAGNOSTIC and
  descriptive, not production-run probabilities.
- **Lead bench.** The **D-117 decision-index CI break** —
  self-inflicted (the decision body landed without its index row) and
  self-caught; the U4 trailing-slash scope-glob launch failure; and the
  **paper fidelity corrections applied by hand** against the code
  (interval-average integration replacing "trapezoidal", the exact
  operative bracket formula, custody-claim narrowing,
  operator-quarantine wording).

### Instrumentation notes

**Fast mode is a real per-call tier, and only on one route.**
`CODEX_SERVICE_TIER=fast scripts/codex-bridge` genuinely sets the
service tier per call (~1.5x speed, 2.5x credits); `codex-run-v3` does
**not** read the variable — verified this session — so audited,
enforced-WRITE_SCOPE implementation runs take the standard tier by
construction. That is the correct split and was ratified as a
deviation note in the plan freeze: fast for read-only fan-out (lenses,
scouts, ideation, drafting), standard for invariant-bearing code.
**A Sol OUTPUT was blocked by a content classifier** for the first time
— adversarial-audit vocabulary in the U1 delta re-audit's final message
(previously only ever observed on input) — recovered by resuming the
same session with a neutral-language, conclusions-only re-emission;
the recovered verdict is what stands in the custody record.

### Dispositions and open state at close

Paper merged (PR #110, `6a70707`) with demonstration values pending the
D-117 windows by construction and explicit pending markers in the
draft. D-117 transcribed and the plan freeze ratified (three toolchain
blockers stand before any arm). Portfolio arc **adopted**: MVP + Window
C → P2 quantization BF16/Q4/Q8 → MoE stretch (re-anchored, desk-gated),
with 7 night-cheap riders folded into the MVP and the rest killed with
salvage recorded. U1 (`impl/d117-u1-ledger-session`) and U3
(`impl/d117-u3-pinset-v2`) are pushed and **await their final gates**;
U1's FIX-6b and U3's delta are the next spends. **Ed's ranked rulings
##1-7 are OWED** — §6/Window C funding, reported-energy cells before
the pack hashes freeze (time-critical), reason-code plumbing before
night one, the 256-token prefill arm, the P2 commitment, calendar
dates, and public-artifact scope — all recorded in
`docs/strategy/2026-08-07-paper-portfolio/ADJUDICATION.md`.


## C-050b: The evening double-window — two merges under the maturing gate, two adopted shapes, and the remand that proved the refuter's seat (2026-08-07/08)

Session: Fable magistrate, resumed cold from the /clear checkpoint
(`a871c9b`), ~3.5h + two extensions on Ed's word; fast tier spammed on
every read-only Sol run per directive. Full records: RUN_STATE EVENING +
EXTENDED + D-121-era blocks (this session's running record),
`docs/process_traces/2026-08-07-d117-u-units/RECOVERY-SHAPE-CONSULT.md`,
`docs/process_traces/2026-08-07-plan-factory/PACK-LAUNCH-CONTRACT-CONSULT.md`,
`docs/process_traces/2026-08-07-u2-coldgate/` (both sealed rulings +
SYNTHESIS), PR #114/#115/#116 gate ledgers, D-119..D-121.

**Merged:** #114 (paper trust language; delta FAIL -> conservative fix ->
ACCEPT + final-head PASS), #115 (U1 night fixes; the port's paired
lenses CONVERGED on a one-sided session-endpoint P1 the original
delta-verified round had missed — fixed at the bench, delta ACCEPT
same-signature NO), #116 (reason-code plumbing; the first merge through
the complete 12-item D-121 gate, magistrate terminal review recorded).

**Adopted:** the ledger-resident recovery shape (sidecar journal
deleted; three rounds of prior work discarded rather than patched); the
typed stage-launch pack contract (U5-U7 amendment 3). U11 chartered
(amendment 4). D-120 (trust closure) and D-121 (terminal magistrate
review) minted; D-121 was exercised same-session on #116.

**The U2 remand (the entry's headline):** cold Fable judge ruled 7
RATIFY / 3 AMEND / 2 DEFER; the adverse Opus refuter proved the packet
quoted D-102/D-116 while the exhibit's own `SUCCESSOR_DECISION_IDS`
declares D-102/D-109/D-117 — D-109's rulings are operative for seven of
twelve questions the judge answered without them. Outcome: NOT
RATIFIED, packet remanded; convergent technical blockers bind the
rework (Q2 screen source, Q3 kernel verification, Q11 fabricated
successor_probe, Q6 abandoned-row brick, Q9 barrier, Q4 one-way door,
allowance rule as new Q13). New packet rule: quote every entry the
exhibit itself declares as authority, mechanically diffed. Charter
erratum #2: worktree convening does not suppress harness injection for
subagents — the disclosure line is the working control.

**Open at close:** trust fix round 2 (window-anchor closure; escalation
tripwire at count 2) and the recovery resume (scope expansion ruled:
receipt-cadence doubling is a design consequence; derived-count fixture
discipline) both in flight; U5-U7 receipt oracles flagged
stale-on-recovery-landing before any pack freeze.

**Lead errors (closed structurally):** a repo-cwd Opus reviewer
detached the main tree via checkout and a bookkeeping commit landed on
the detached lineage (cherry-pick recovery; rule: reviewers get
worktree isolation + pre-commit branch check); the lead's first replay
was piped — the twice-recorded rule recurred and the replay was redone
unpiped.

## C-051: The T0 window — three streams, a mid-run kill, and the fixture the push refused (2026-08-08)

Session: Fable magistrate, morning → ~13:40, ended mid-run by Ed's stop
order; three parallel Sol streams (trust/recovery/u2rework worktrees)
under enforced WRITE_SCOPE plus a read-only consult lane. Entry written
post-session by a successor bookkeeping agent under the dictated-fills
pattern (facts verified against the primary evidence; anything
reconstructed is labelled in the run report). Full records: run report
`docs/run_reports/2026-08-08-t0-window-session.md`, RUN_STATE T0 FINAL
CHECKPOINT (`18d007a`), scratchpad consults
(trust-RULING-CONSULT/ESCALATION, recovery-WITNESS-SCOPE-RULING/
ESCALATION, u2-SYNTHESIS-V2, checkpoint-notes.md),
`docs/process_traces/2026-08-08-recovery-exits-escalation/` (gauntlet
lenses + triage, on the recovery branch), U2-FROZEN-COUNT3.md
(`5b00200`), D-126/D-127/D-128.

**Merged:** results-prose template + fail-closed linter (`1e6fa16`) —
the unconditional-assertion class ruled DEAD after 4 delta rounds; the
only fully gated landing of the session. **Banked UNGATED:** trust
round 2 at `1cae2bc` (mid-run kill at ~4h22m; worktree diff is ground
truth; round-2 proofs NOT run); recovery FIX-1..13 at `468e0a6` (2770 OK
in-run per the report; delta re-audit owed). **Frozen:** U2 at
attestation count 3.

**Deliberations that decided things:**

- *Trust F1/F2 ruling consult* — the magistrate presented its proposed
  R1/R2 with explicit license to disagree and was out-designed on both:
  boundary pre/post hashing rejected on a concrete A→B→A TOCTOU proof in
  favor of a registration-aware path capability; the relocation table
  rejected for a content-addressed custody store keyed by receipt
  content_id with manifest-vs-ledger equality. ADOPTED IN FULL,
  superseding (`fe85b09`); the 7-step sequencing bound the resumed
  round. Another rule-2 data point: invited design judgment beat the
  lead's proposals.
- *Recovery triage (consult-vs-fix)* — with the ungoverned-refusal class
  already escalated at count 2 (exit-completeness consult →
  witness-scope ruling `6981d2b`), the gauntlet's two NEW prohibited
  shapes (unexecuted-proof-reference; inspect-as-permission) were each
  ruled FIRST occurrence, count 1 — licensing exactly one dictated fix
  round with the count-2 → consult rule pre-armed in writing for the
  next delta.
- *U2 count-3 freeze* — the delta ruled the attestation-binding class
  same-signature YES a third time with an executed forgery (ledger-absent
  epoch accepted as `VerifiedAcceptance`; enrollment auto-generated with
  always-true verifiers). Per rule 11 the answer is a deliberate cold
  gate, not fix round three; the freeze costs the paper nothing
  (issuance already gated behind Q12 + the third convening).
- *Mid-run kill adjudication* (Ed's stop order at ~4h22m of trust
  round 2) — bank the worktree diff as an explicitly UNGATED checkpoint
  with a written trust-nothing rider enumerating the six unrun round-2
  proofs, rather than let a truncated run (report absent, status
  ACCEPTANCE_FAILED) pose as a result.

**Unique catches by layer:** gauntlet lenses A/B — round-3-introduced
production defects, reproduced (aliased-lock double lease; POST
readiness blind to PRE custody corruption; pin advancement admitting a
pending business head): the fix-rounds-introduce-defects doctrine held
again. U2 delta — the Potemkin enrollment (a catch that terminated a
stream). Magistrate bench — the recovery harness's own 8-orphan SIGKILL
leak (an instance of the exact orphan class the stream governs), kept
OUT of the live fix round per the two-writers rule and routed to the
successor delta with a timing-distortion question over the suite
numbers; and the fixture-size blocker (~3.1 GB, 38 content-IDs) surfaced
by the GitHub push warning → new substrate ruling opened. Ed — the stop
order itself.

**Escalation discipline (the entry's headline):** the same-signature
trigger fired three times across 2026-08-07/08 — trust delta classes at
count 2, recovery ungoverned-refusal at count 2, U2 attestation at
count 3 — and all three were honored: consult, consult, freeze. No
round-3 fix was attempted anywhere. The rule-11 shape (escalations
redirected to consults instead of eaten) ran clean for a full window.

**Dissents:** none recorded; both adopted rulings superseded magistrate
proposals without magistrate dissent.

**Follow-ups:** fixture-substrate ruling (blocking trust); recovery
delta with the three questions → replay → integration → PR (arming
blocker); U2 cold gate post-window; D-127 build adoption; assertion-61
pre-patch determination before the wrapper retention patch re-lands;
consistency sweep after the next merge wave. Spend snapshot: NOT
captured — the session was killed before entry close and the successor
agent cannot reconstruct per-tier spend; noted as a gap rather than
estimated.

## C-052: T1 — the substrate ruling, the fast default, the recovery freeze/cold-gate arc, and the trust verification wall (2026-08-08)

Session: Fable magistrate under D-128, continuing T0's Phase-A recovery/trust frontier with a desk bookkeeping lane; the trace records disjoint recovery, trust, and main-tree footprints, later expanding recovery to six parallel graders and two fresh cold-gate judges. (Evidence: `trace-notes.md` §§0, “Shape”, “Launches”, and lines 105–113/167–194.) Exact overall session wall time is **UNVERIFIED**; `RUN_STATE.md` records the night stop order and no processes left in flight. (Evidence: `RUN_STATE.md` lines 49–55.) Full records: T1 `trace-notes.md`; `RUN_STATE.md` lines 49–187; main commits `8788891`, `b7aad49`, `de759c9`, `2ba514a`, `d071a3d`; recovery commits `721593b`, `bc01908`, `4495609`, `0c30993`, `e265c9c`; trust checkpoint `1cae2bc`; and the supplied 2b/2c manifests and recovered report. (Evidence: `git log d81c78a..d071a3d`; recovery branch log `468e0a6..e265c9c`; manifest line 1 records.)

**What shipped and what did not.** The session shipped the fixture-substrate ruling/addendum, tracked bridge fast-default change, recovery escalation and cold-gate custody, and consistency fixes; it did not ship either recovery or trust through PR/CI/D-121/merge. (Evidence: `RUN_STATE.md` lines 57–101; `git log d81c78a..d071a3d`; `e265c9c`.) The primary recovery merge/ARMING discharge therefore remained open, while the trust stream was design-unblocked but verification- and integration-incomplete. (Evidence: `trace-notes.md` §0; `RUN_STATE.md` lines 58–89.)

### Substrate ruling

The substrate consult rejected the listed Git-as-is/LFS-style choices in favor of release-asset hydration: the trace records 3.087 GiB of plists compressing to ~142 MiB, eight full CI checkouts under Git-as-is, and LFS metering raw bytes; the magistrate adopted the consult in full. (Evidence: `trace-notes.md` lines 42–45; ruling `8788891`.) The ruling requires a digest-pinned tar.zst asset, hydrator, census manifest, and production-proof CI job, with 38 content directories removed from Git history later under a lease-guarded rewrite. (Evidence: `8788891` commit message; `RUN_STATE.md` lines 81–87.)

Two lead-side rewrite attempts were denied by the classifier; the lead honored the denials, created a safety tag and verified 53-MB bundle, deferred the rewrite, and proceeded tooling-first. (Evidence: `trace-notes.md` lines 46–60; addendum `b7aad49`.) Ed later granted four rewrite permission rules, but the rewrite remained deferred until after trust harvest and still had not occurred at close. (Evidence: `trace-notes.md` lines 57–60; `RUN_STATE.md` lines 84–89/103–109.)

### Fast-mode standing default and parallelism ruling

Ed directed fast mode everywhere for Codex, not Anthropic, with Claude/Fable kept scarce and lean; the tracked bridge changed to fast by default, `CODEX_SERVICE_TIER=default` became the opt-out, and the machine-local v3 wrapper was changed in place with a backup. (Evidence: `trace-notes.md` lines 87–96; `de759c9`; `RUN_STATE.md` lines 123–130.) The trace records a smoke test observing `service_tier=fast` on the child command line and successful output; independent post-session re-verification of the machine-local wrapper is **UNVERIFIED**. (Evidence: `trace-notes.md` lines 91–94.)

Ed also made harder parallelism the standing direction: read-only work fans out, implementation parcels by disjoint footprint, and a monolith requires a named reason. (Evidence: `trace-notes.md` lines 87–99; `RUN_STATE.md` lines 103–106.) The session supplied the motivating counterexample: trust 2b bundled separable substrate/auth work into an eight-hour monolith, while the six-lens recovery delta showed the new fan-out shape's yield. (Evidence: `trace-notes.md` lines 97–113/147–158; `trust2b-out.manifest.jsonl` line 2.)

### Recovery: failure → escalation → freeze → cold gate → ruling

Delta 1 failed FIX-1..13: unexecuted-proof survived at count 2; hard-link lease aliasing, late preservation sampling, lint blindness, and a confirmed orphan leak formed the convergent under-proof signature; inspect-as-permission was ruled dead. (Evidence: `721593b`; `trace-notes.md` lines 61–70.) The rule-11 trigger fired, so the lead convened ESC-2 rather than authorizing a reflexive fix round. (Evidence: `trace-notes.md` lines 61–75.)

ESC-2 was adopted in full: dual slot/object lease identity, two-invocation binding-conflict evidence, a universal preservation guard, owned public-process execution with double-keyed crash capability, a receipt corpus/provenance analyzer, and the 17→15→16→14→18 implementation order; the magistrate added the RefusalCode registry/witness/census rider. (Evidence: `bc01908`; `trace-notes.md` lines 76–83.) The resulting FIX-14..18 implementation reported mutations killed and `2785 OK`, but remained ungated. (Evidence: `4495609`; `trace-notes.md` lines 100–104.)

Delta 2 then returned all six lenses NOT-CLOSED. G1 reproduced the unexecuted-proof class at count 3; G2 found genesis staging/publication not dirfd-bound; G3 executed a deferred-fingerprint timing mutation; G4 found a process-runner inherited-pipe hang; G5 found analyzer laundering; G6 found cleanup that could unlink an invalid supplied path. (Evidence: `0c30993`; `trace-notes.md` lines 121–145; `e265c9c` synthesis item 2a.) The repeated lease and preservation families came after a “terminating” consult, satisfying the mandatory cold-gate trigger and prohibiting an automatic FIX-19. (Evidence: `trace-notes.md` lines 137–145.)

Both cold instances independently reproduced G1's count-3 bypass. (Evidence: `e265c9c:docs/process_traces/2026-08-08-recovery-exits-escalation/COLD-GATE-SYNTHESIS.md`, “Both instances agree.”) The cold Fable adjudicator ruled the FIX-14 claim category-false: Python has no in-process trust boundary capable of making test evidence unfabricable through source gates, so additional AST evasion patches cannot terminate the class. (Evidence: same synthesis section.) The Opus refuter ruled a bare clean-core landing unsafe because the lease seam/G2 lived in the core and the pre-arming corpus was forgeable; it also caught the packet's contradictory G2 first/second-occurrence labels and refined G6's arming severity. (Evidence: `trace-notes.md` lines 175–191; synthesis “The split” and final paragraph.)

The magistrate synthesized rather than erased the dissent: both positions rejected landing as-is; the adopted path licenses one executed-probe production/support round for G2, G6, and G4, followed by D-117 manual arming and lead live verification. (Evidence: `e265c9c` synthesis, “MAGISTRATE RULING” item 2.) Witness integrity moved off the critical path to an out-of-process mutation-kill harness; AST/corpus gates remain only as drift lint, with an L1 limitation that the corpus does not certify against an adversarial in-repo test author. (Evidence: same synthesis items 3–4.) Another lease facet after the G2 fix escalates to an IDENTITY-MODEL consult. (Evidence: same synthesis item 5.)

The ruled G2/G4/G6 round was killed before writing; no recovery merge or ARMING discharge occurred. (Evidence: `RUN_STATE.md` lines 58–69; `d071a3d`.)

### Trust: 2b wall and 2c verification tail

Trust 2b ran Sol xhigh for 28,803,970 ms from `1cae2bc`, changed 12 in-scope paths, incurred no scope violation, and ended `ACCEPTANCE_FAILED` solely at missing report capture. (Evidence: `trust2b-out.manifest.jsonl` lines 1–2.) The recovered report records passing reduce.py SHA, ABA, absent-mode parity, 14/7/7 authentication/custody/transport suites, four V2 pinset tests, 190/190 census, archive self-verification, and one authentic unpatched production mint as an internal stage. (Evidence: `trust2b-report-recovery.md` V1–V6 and “Verification notes.”)

The decisive regression itself failed after 4,056.083 s in the test-only open auditor, before full production equality and before the coordinated attack/mutation matrix. (Evidence: `trust2b-report-recovery.md` V7/flag F1.) A repaired-auditor diagnostic later reported 193/193 equality, but the report explicitly denies that this substitutes for the interrupted final proof. (Evidence: its “Bidirectional production open/registry equality” section.) V1 parity, final focused verification, `git diff --check`, and the full suite were not run. (Evidence: V8–V9/flag F2.)

The built archive measured 3,333,877,627 logical bytes and 191 logical files with SHA `f1286bc…`; a draft release asset was uploaded and freshly downloaded with a matching SHA, but publication remained gated on lead verification/hydrator census. (Evidence: `trust2b-report-recovery.md` “Change”; `trace-notes.md` lines 114–116; `RUN_STATE.md` lines 81–86.) Independent lead verification and publication are **UNVERIFIED**. (Evidence: recovered report F4.)

Trust 2c ran Sol high for 3,782,506 ms from the same head with an 18-path verification scope, changed no paths, and again ended `ACCEPTANCE_FAILED` at missing report capture with semantic status/completion unknown. (Evidence: `trust2c-out.manifest.jsonl` lines 1–2.) `RUN_STATE.md` says the tail ran and should be harvested from disk, but no supplied primary artifact establishes any 2c test result; every claimed 2c proof is **UNVERIFIED**. (Evidence: `RUN_STATE.md` lines 73–80; 2c manifest line 2.)

### Unique catches by layer

- **Substrate Sol design consult:** found the release-hydration shape that the listed options missed; adopted in full. (Evidence: `8788891`; `trace-notes.md` lines 42–45.)
- **Recovery delta 1:** caught the surviving unexecuted-proof mutation, lease alias, preservation timing, lint blind spot, and real orphan leak; killed inspect-as-permission. (Evidence: `721593b`; `trace-notes.md` lines 61–70.)
- **ESC-2 Sol design consult:** rejected single-key identity and supplied five exact terminating contracts plus sequencing. (Evidence: `bc01908`; `trace-notes.md` lines 76–83.)
- **Recovery implementer:** caught that `git diff` omitted four untracked support files before commit. (Evidence: `trace-notes.md` lines 100–104.)
- **Delta-2 G1:** executed the EvidenceAlias/direct-readiness fabrication and established count 3. (Evidence: `0c30993`; `e265c9c` “Both instances agree.”)
- **G2:** found the never-executed genesis dirfd-binding miss; the cold synthesis resolved it as second occurrence of the family but first missed genesis call-site. (Evidence: `trace-notes.md` lines 121–123/184–188; `e265c9c` final paragraph.)
- **G3:** executed the manifest-corruption/deferred-fingerprint timing bypass. (Evidence: `trace-notes.md` lines 124–126.)
- **G4:** found the inherited-pipe runner hang. (Evidence: `0c30993` commit message; `e265c9c` item 2a.)
- **G5:** found kw-only-helper and nested-comprehension analyzer laundering. (Evidence: `trace-notes.md` lines 127–128.)
- **G6:** found unlink-on-validation-failure destruction; Opus later refined it from blocker to should-fix for arming reachability. (Evidence: `trace-notes.md` lines 129–131/189–191.)
- **Cold Opus refuter:** caught the G2 packet contradiction and forced the lease-core/F1 decomposition objection into the final ruling. (Evidence: `trace-notes.md` lines 175–188; `e265c9c` “The split.”)
- **Cold Fable adjudicator:** caught that the claimed in-process property was unattainable and replaced it with an out-of-process mutation-kill property. (Evidence: `e265c9c` “Both instances agree”/item 3.)
- **Trust implementer/test tail:** exposed a 68-minute irreducible test atom and the `/dev/fd` no-follow auditor bug after authentic mint. (Evidence: `trace-notes.md` lines 147–158; `trust2b-report-recovery.md` V7.)
- **Lead/Ed:** honored classifier denial, preserved custody, held release publication, changed fast/parallel policy, and stopped all processes at close. (Evidence: `trace-notes.md` lines 46–60/87–99/114–116; `RUN_STATE.md` lines 49–51.)

### Deliberation resolutions and dissent

The substrate design was adopted in full without recorded dissent. (Evidence: `trace-notes.md` lines 42–45; `8788891`.) The cold gate preserved a real disagreement—Opus UNSAFE versus Fable GRANTED—but the synthesis reconciled it because both rejected a bare merge; the Fable path was adopted with the refuter's seam/F1 objections as mandatory reasons for the fix round and limitation. (Evidence: `e265c9c` “The split.”) The synthesis records no magistrate dissent from the cold-instance verdict. (Evidence: `e265c9c` final paragraph.)

### Process findings and follow-ups

The first ESC-2 launch repeated the documented literal-`WRITE_SCOPE` failure, and parallel `--write-scope` launches exposed a per-worktree scoped-runner lock; the workaround was prompt-line scope plus post-harvest clean-status verification for read-only graders. (Evidence: `trace-notes.md` lines 71–75/108–113.) Security-vocabulary tier instability blanked G2 until neutral software-engineering wording was used, motivating neutral-SE refuter phrasing. (Evidence: `trace-notes.md` lines 132–135.) The trace and final checkpoint report folds for parcel-by-footprint, neutral wording, scoped-lock handling, and parallelism-by-default, but independent current skill-file verification is **UNVERIFIED**. (Evidence: `RUN_STATE.md` lines 97–100.)

**Follow-ups:** recovery G2/G4/G6 fix → scoped delta → replay/integration/PR/CI/D-121/merge/manual arming; trust worktree harvest → load-bearing reruns → commit split → release publication → history rewrite → 16-question delta → PR; U2 remains post-window frozen. (Evidence: `RUN_STATE.md` lines 57–90.)

**Yield/spend:** the trace names at least 15 model-bearing lanes/roles plus one instant failed wrapper launch, but exact launch count and whole-session cost are **UNVERIFIED**. (Evidence: `trace-notes.md` “Launches,” lines 71–113/147–194; cold synthesis.) Trust 2b and 2c exact runner durations were 8:00:03.970 and 1:03:02.506; both manifests record `token_usage:null`. (Evidence: each manifest line 2.) The recovered 2b transcript ends with `1,909,882` tokens, but its billing meaning and relation to resumed context are **UNVERIFIED**, so no total-spend claim is made. (Evidence: `trust2b-report-recovery.md` final line.)

## C-053: T2 — five merges, the mint proof, and the seam not rushed at hour nine (2026-08-09)

Session: Fable magistrate, approximately 23:30 → 08:30, resuming T1's recovery/trust frontier with disjoint recovery, trust-report, three pack, and bookkeeping lanes. The work expanded into a 30-agent pack review and family harmonization, operator/results/methods paper lanes, decomposed trust verification, trust landing-design/conflict/R1 reviews, and a recovery-flake lane; nothing remained in flight at Ed's checkpoint. Exact endpoints beyond the trace/checkpoint's approximate labels are **UNVERIFIED**. (Evidence: T2 `trace-notes.md` lines 1–22/42–55/77–171/203–227; `RUN_STATE.md` lines 49–54.) Full records: `docs/run_reports/2026-08-09-t2-window-session.md`; the named custodied T2 trace and Sol reports; `RUN_STATE.md` T2 FINAL/UPDATE blocks; merge commits `06303b5`, `05ce39b`, `d48fc81`, `0ab71f4`, and `fc53105`; and the two ruled strategy plans.

**What shipped and what did not.** Five PRs merged: #117 the three unfrozen D-117 packs, #118 recovery/arming code plus §5C procedure, #119 operator arm-readiness, #120 results scaffold, and #121 methods plus draft corrections. Suite repair `55a05e3`, prose-linter Python 3.11 repair `b3a5008`, and T1 bookkeeping `01420da` also landed. Recovery's code-and-procedure side of ARMING discharged. Trust's mint bar was PROVEN, but clean-main assembly, public release publication, PR/CI/D-121, and merge did not occur; pack freeze and live arming also remained open. (Evidence: `git log d071a3d..5c78167`; `RUN_STATE.md` lines 56–106/108–167.)

### Recovery and the counter-reviewed arming procedure

The cold-gate-licensed fix closed G2/G6/G4 by executed probe, then its scoped delta found new retry-then-trust fsync and Darwin teardown defects rather than repeating the production signatures. G5 analyzer evasion was kept as cold-gate-demoted drift lint, not used to smuggle prohibited FIX-19 work back onto the critical path. The second round closed the new defects and PR #118 merged. (Evidence: `trace-notes.md` lines 97–100/117–140; commits `ee2db0b`, `706173b`, `05ce39b`.)

Sol's counter-review found six errors in the lead-authored §5C procedure; all six were adopted, including §5B's in-chain position, removal of a fictional readiness field, chain-owned final settle, single-authority GO record, observable live-verification events, and typed refusal routing. This was the session's clearest dual-prior result: the lead kept authority and changed its own plan when the independent design was better. (Evidence: `trace-notes.md` lines 102–115/129–140; `a2f7850`.)

### Trust: proof, safe landing design, and R1

The first decisive rerun failed in the test's attack leg after 6,313 seconds because it assumed a guarded floor could not be `None`; the stronger fabricate-if-absent tamper replaced that assumption. The next approximately 3.5-hour run exercised all 15 attack domains and every domain refused, but twelve expected-fragment checks failed. Sol triage separated eleven stale canonical fragments from one real coverage shadow: `primary` was refused by evaluation-basis validation before the intended complete-bundle discriminator ran. The shadow leg was reworked and isolated-proven, so the magistrate ruled the mint bar PROVEN without pretending the fragment errors were all harmless. (Evidence: `trace-notes.md` lines 148–188; `trust-triage-out.md` lines 31–40/75–96; `RUN_STATE.md` lines 63–70/115–123.)

Landing design then caught that T1's recorded `git rm --cached` plus amend would leave the 3.3-GB custody objects in parent ancestry. Clean-branch resynthesis with a real three-way merge and a single-parent `commit-tree` replaced it. (Evidence: `trace-notes.md` lines 190–201/246–271; `trust-landing-design-out.md` D1–D3.) The first merge attempt exposed nine recovery-added direct-I/O sites against trust's registration-at-read guard, so the lead aborted the throwaway merge rather than rush a security classification at hour nine. A fresh R1 cycle routed three content-bearing evidence reads through `read_authentication_input` and narrowly classified six descriptor/OS-metadata sites with separate line-anchored justifications; 14 guard tests and 106 focused tests passed in-run. The resolved files were custodied for final assembly. (Evidence: `trust-conflict-out.md` R1; `trust-r1-out.md` “Change”/V1–V4; `RUN_STATE.md` lines 62–84/126–141.)

### Pack freeze and the “better paper” rule

The magistrate ruled Q2A/Q2B/Q2C/Q3/Q4/Q7 and converted the remaining gaps into four work orders: FLOOR-COMMONMODE-01, D-123 production-byte identity, receipt-oracle re-derivation, and prefill phase-recording proof. Ed then closed both taps: Q1 freezes the recommended dual-tokenizer-identical 256-token prompt (token-ID SHA prefix `83099a66`), and Q8 funds dedicated p256 floor cells because no p128→p256 transport is allowed. The standing discretionary tiebreaker is the “better paper.” (Evidence: `docs/strategy/2026-08-09-pack-freeze-plan.md`; `packfreeze-packet-out.md`; `e02c4ca`.) The plan's older body still says the taps remain pending even though its opening banner, the commit, and final checkpoint record them ruled; this stale pre-tap wording is an explicit source anomaly, not an open decision.

### Unique catches by layer

- **U5/full-suite lane:** found three stale expectations left by T1's fast-default and kernel changes; `55a05e3` restored suite-green. (Evidence: `trace-notes.md` lines 57–64.)
- **U7 implementer:** correctly early-returned when the decode-only scout instruction contradicted D-122; the relaunch built both gamma arms. (Evidence: `trace-notes.md` lines 211–219; `e286e75`.)
- **Pack review/refuter:** found family-wide schema/vocabulary divergence from parallel authorship and killed five plausible false findings; harmonization and two fix rounds preceded merge. (Evidence: `trace-notes.md` lines 77–100; `06303b5`.)
- **Recovery delta:** distinguished closed G2/G6/G4 signatures from two new production defects and kept G5 off-path per the cold ruling. (Evidence: `trace-notes.md` lines 117–127.)
- **Sol counter-review:** corrected all six substantive errors in the magistrate's manual-arming draft. (Evidence: `trace-notes.md` lines 102–115/129–137.)
- **Lead fleet-health check:** inspected the process tree and avoided killing CPU-active mint children hidden behind idle unittest parents. (Evidence: `trace-notes.md` lines 141–146.)
- **Trust test/triage:** caught the test's `None` assumption, then the eleven stale fragments and one real coverage shadow while preserving the all-15-refused security result. (Evidence: `trace-notes.md` lines 148–188; `trust-triage-out.md`.)
- **Landing design/conflict/R1:** prevented a dirty-ancestry landing, discovered the nine-site trust×recovery seam, and resolved it as three authenticated reads plus six narrow classifications. (Evidence: `trust-landing-design-out.md`; `trust-conflict-out.md`; `trust-r1-out.md`.)
- **Pack-freeze review and Ed:** proved the p256 prompt identity, refused unsupported floor transport, funded the claim-capable floor cells, and made “better paper” the tiebreaker. (Evidence: `packfreeze-packet-out.md`; pack-freeze plan.)
- **Flake-fix lane:** traced `.git/objects` teardown failures to unreaped holder process groups and proved the fix with 30/30 lifecycle stress plus focused/full suites. The fix was banked and pushed as `5a8a200`, not merged. (Evidence: `flakefix-out.md`; `RUN_STATE.md` lines 85–89.)

### Deliberation resolutions and dissent

No unresolved model-held dissent is recorded in the named sources. The pack family's divergence was resolved by lead-pinned interchange choices and harmonization. The arming-procedure counter-review displaced the lead draft on all six findings. Trust triage rejected the easy “all stale fragments” answer by preserving the one category-B shadow, while later landing work kept proof and integration as separate gates. The deliberate hour-nine deferral was not indecision: marker resolutions were known, but the security seam required a fresh adjudication cycle. (Evidence: `trace-notes.md` lines 77–140/173–201; three trust reports.)

### Process findings and follow-ups

Parallel family authorship without an interchange pin produced three incompatible member encodings and related vocabulary drift; future family prompts need a common interchange spec or an explicit harmonization round. Mint-grade workload monitoring must inspect child processes, and no more than two mint-grade suites/legs should run concurrently on this machine. Long verification tails should be decomposed where state can be byte-matched, while the authoritative final-head suite remains serial. (Evidence: `trace-notes.md` lines 77–89/141–171/221–228.)

**Follow-ups:** verify and merge `impl/recovery-flake-fix`; assemble trust against current main with the custodied R1 resolutions; prove blob-free ancestry, run the full suite, publish the release, pass `d117-production-proof`, D-121, and merge; then land FLOOR-COMMONMODE-01, collect the Ed-funded p256 floors in a quiet window, close the remaining freeze proofs, regenerate/freeze packs, and arm only through §5C. (Evidence: `RUN_STATE.md` lines 62–106.)

**Yield/spend:** the trace reports one 30-agent review wave at approximately 2.16 million tokens over 19 minutes. That is workflow-local, not a total-session cost. The sources do not supply a complete runner census or summable billing records, so exact whole-session spend and exhaustive launch count are **UNVERIFIED**. (Evidence: `trace-notes.md` lines 77–81 and the absence of a whole-session spend record.)

**Source cautions:** `trust-r1-out.md` ran from an integration base six commits behind then-current `origin/main`, so its 3/6 ruling and focused proofs do not replace final assembly against current main or the full suite. The last local decisive rerun wedged; the authoritative clean-branch CI proof remained pending. Recovery's green full-suite reports carried an environment-dependent skip-count difference (90 versus 86). `flakefix-out.md` predates the later banked commit, so its “no commit created” statement and the final pushed-branch state are successive observations, not a merge claim.

## C-054: T3 — the flake merge, two decisive-CI rounds root-caused, and the mint bar one gate away (2026-08-09)

Session: Fable magistrate, approximately 08:30 → 21:35 on 2026-08-09, resuming directly from the T2 checkpoint. It was the first full session under D-129 and ran at a recorded peak of about nine concurrent streams: bench flake verification and the PR #123 merge; trust guard and decisive-CI fix lanes on `impl/d117-postcollection-trust-clean`; a read-only Sol diagnosis of the round-1 CI failure; WO-4, WO-2, and FLOOR-COMMONMODE-01 implementation lanes in disjoint worktrees; a six-lane Sol extension-axes workflow with an xhigh synthesis (`wf_d35129b8-58c`); an Opus-validated read-only consistency sweep; and Opus grader/refuter fleets for the 16-question trust delta. The decisive trust CI was still in flight when Ed called the wrap. (Evidence: `flake-loop.log` first iteration 08:32:54; `git log` `7fde68b` 08:57 → `24c5e26` 21:35; `RUN_STATE.md` lines 50–115.) Full records: `docs/run_reports/2026-08-09-t3-window-session.md`; the custody set `~/JouleWise-window-custody/t3-session-20260809/`; commits `cace694`, `7fde68b`, `966dd39`, `e9c2433`, `2cd9bc3`, `955df9b`, `50d1064`, `f7117e1`, `24c5e26`; branch parcels `e376e8c`, `99d0e9b`, `e807d5f`, `f588f86`, `e871f5b`; and `425f75f`.

**What shipped and what did not.** Merged or landed on main: the calibration-exits flake repair (PR #123, `cace694`), T2 bookkeeping and its council-index repair, the WO-4/Q9 prefill phase-recording proof, the H1/H2 extension-axes roadmap as a DRAFT, the site-renderer truncation fix, and the consistency sweep with D-129 and the state-kernel gate move to `T3-2026-08-09-DAY`. The production fixture release was published and its digest re-verified. Not shipped: the trust merge that lifts the mint bar (PR #122 left at `e871f5b` with the decisive CI in flight), WO-2 (PR #124 opened, not merged in-session), FLOOR-COMMONMODE-01 (banked **ungated** at `425f75f`, magistrate audit and D-118 gauntlet owed), and WO-3 (not started). (Evidence: `RUN_STATE.md` lines 58–101; `gh release view fixture-d117-v2-production-v1`.)

### Trust: two decisive rounds, both root-caused, hermeticity kept strict

The 16-question delta closed 16/16 after a fix-then-regrade on Q10 and Q3. Its blocker was that the registration-at-read guard could not see readable `os.fdopen`; its should-fix surfaced two unclassified writer-lease repair scans and, more sharply, falsified a classification the T2 magistrate had already approved — `open_append_descriptor`'s “append handle” justification was contradicted by its own callers and was rewritten honestly rather than preserved. The re-grade of those fixes then produced residuals of its own: `io.open` and `codecs.open` were misparsed by the bound-method branch, with the path argument read as the mode, so `io.open('led.bin','rb')` passed unseen; and the `fdopen` fail-closed default was pinned by no test, so a refactor could have silently reopened the hole with CI green. Guard tests went 16/16 then 18/18 on both 3.11 and 3.13. (Evidence: `99d0e9b`; `f588f86`; `guardfix-report.md` V1–V8; `RUN_STATE.md` line 74.)

Decisive CI failed twice, and neither failure was allowed to become a narrowed assertion. Round 1 was adjudicated **latent, not merge-introduced**: the campaign never received the hydrated custody store, and T2's green local runs had silently read Ed's machine-local and iCloud paths that CI lacks — the read-only diagnosis reproduced the CI refusal on both 3.13 and 3.11 by hiding only those historical paths. The fix threaded a store-exclusive `--calibration-custody-store` option through minted whole-window evaluation and added a hermeticity assertion with its own exit code 2, so a hermeticity failure can never be read as an expected refusal. Round 2 was that new assertion firing on a second unplumbed read site: `discover_calibration_candidates()` reauthenticated through `observation.custody_locator` at `calibration_bracketing.py:961`. Census evidence — 38 content IDs across five governed artifacts, plus the twenty pre/post content directories the builder adds — showed every firing identity was store-served, so resolution (a), fixing production, was adopted over resolution (b), narrowing the assertion; the forbidden legacy-locator set was left untouched. (Evidence: `sol-diag1.md` summary/F2; `e807d5f`; `ci-fail-round2.log` line 6; `fix2-report.md` “Change”; `e871f5b`.)

A separate CI catch belongs to the 3.11 leg alone: `_floor_estimate`'s squared-residual reduction used `builtins.sum`, whose float behavior changed in CPython 3.12, so 3.11 differed by one ULP and broke the exact-golden extraction report while 3.13 and 3.14 passed. `math.fsum` restored agreement across all supported interpreters. (Evidence: `e376e8c`.)

### The freeze lane

WO-4/Q9 discharged with the resolution distinction intact. Across 100 bundles, raw `powermetrics.plist` reconstructed `power_trace.csv` exactly and independent interval-support reintegration reproduced every stored prefill energy exactly, at 0.0 J maximum absolute discrepancy on both stacks. 7B is PROVEN at 50/50 `identifiable`; 1.5B is PROVEN-WITH-CAVEATS because 37/50 prefill windows overlap only two power intervals at the ~112 ms cadence against 0.121–0.147 s windows. The mislabeling discriminator ruled that out as a boundary problem — prefill ends before decode start and token 0 on all 100 bundles, with zero overlap and no post-decode interval support consumed — so the caveat was recorded as sampling resolution and forwarded as expected label pressure on the Ed-funded Q8 p256 1.5B cells. The director lead-verified a bit-identical clean-shell rerun and the magistrate's full audit returned ACCEPT. (Evidence: `PROOF.md`; `wo4-sol-out-r2.md` V1–V2/F1; `2cd9bc3`.)

WO-2/Q5 raised both floor packs' reporting-inertness tests to production-canonical byte and SHA-256 identity through the real `extract_detection_floors` wire, replacing 7B's object-equality-only and 1.5B's validation-plus-projection-only proofs, and opened as PR #124. FLOOR-COMMONMODE-01, the freeze long pole, implemented the ratified D-124 two-shared-edge estimator with all six registration conditions structurally enforced and was banked ungated on trust head `8038ccd` with an explicit “do NOT consume” rider. (Evidence: `f7117e1`; `wo2-report2.md`; `425f75f`; `fcm01-report.md`.)

### D-129 and the doc sweep

Ed's three in-thread directives were transcribed as D-129: the standing fan-out order (maximal parallel fan-out is the default whenever it speeds work, including H1/H2 preparation when H0 lanes saturate), the roughly 60% fast-tier cut making the default Codex service tier the norm, and the Fable token economy in which orchestration runs on Opus 5 subagents while Fable's coverage is explicitly unreduced. Clause 3 amends the operative stream-director framing in `docs/orchestration.md` while the C-009/C-010 stamped council consensus is retained as the dated record it is. The accompanying sweep found 22 stale operative statements across seven of nine documents and propagated the tier change to its three homes. (Evidence: `docs/decision_log.md` D-129; `sweep_report.md`; `50d1064`.)

### Unique catches by layer

- **16Q Opus grader/refuter fleet:** found the guard blind to readable `os.fdopen` and falsified a T2-approved classification whose own callers contradicted it. (Evidence: `99d0e9b`; `RUN_STATE.md` line 74.)
- **The re-grade layer:** both re-grades passed, yet their residuals exposed the `io.open`/`codecs.open` mode-position misparse and the untested `fdopen` fail-closed default — defects the original findings had not contained. (Evidence: `f588f86`.)
- **Read-only Sol diagnosis:** proved round 1 was a latent plumbing gap present at `a89f279` by reproducing the CI refusal on both interpreters with only Ed's historical iCloud paths hidden. (Evidence: `sol-diag1.md` F2.)
- **The round-1 fix's own hermeticity assertion:** caught the second unplumbed read site that every green suite had missed, and the census evidence made narrowing it indefensible. (Evidence: `ci-fail-round2.log`; `fix2-report.md`; `e871f5b`.)
- **CI 3.11 leg:** exposed the one-ULP cross-interpreter divergence against the exact-golden extraction report. (Evidence: `e376e8c`.)
- **Site-lane test:** decision-log growth pushed a page past the 64 KiB pipe buffer and converted a silent rc=0 mid-byte truncation into a deterministic `UnicodeDecodeError`; measured as pipe 65,536 B against a 510,214-byte file on identical input. (Evidence: `955df9b`.)
- **Site build parity check:** caught the C-053 index row omitted by the T2 bookkeeping commit — a class the plain suite skips, so council-log edits must run the gated site lane. (Evidence: `966dd39`.)
- **Consistency sweep:** 22 stale operative statements in seven of nine documents, including the pack-freeze pre-tap wording that C-053 had flagged and left open; 12 of 22 findings Opus-validated, RUN_STATE T2-block items deliberately deferred into the session-end checkpoint. (Evidence: `sweep_report.md` F1–F11; `50d1064`.)
- **WO-4 discriminator:** separated a sampling-cadence limitation from boundary mislabeling and converted it into a forward warning for Q8. (Evidence: `PROOF.md`; `2cd9bc3`.)
- **Envelope discipline:** three Sol rounds hit the F3-class read-only-sandbox launcher trap and returned blocked or partial immediately rather than fabricating progress; the protocol held while the launcher configuration cost the rounds. (Evidence: `fcm01-report-blocked-attempt1.md` F1; `wo2-report.md` F1; `wo4-sol-out.md` F1/F2; `RUN_STATE.md` lines 103–105.)

### Deliberation resolutions and dissent

No unresolved model-held dissent is recorded in the named sources. The load-bearing resolution was round 2's: fix production rather than narrow the assertion that had just proven its worth, decided on census evidence rather than convenience. Two other calls declined momentum — FLOOR-COMMONMODE-01 was banked ungated instead of PR'd on its own green report, and the extension-axes roadmap landed marked DRAFT with nothing registered and commitment authority left with Ed under D-075. The standing escalation trigger was armed rather than spent: with two decisive rounds gone, the successor order states that a third same-class failure is a consult, never a round three. (Evidence: `e871f5b`; `425f75f`; `e9c2433`; `RUN_STATE.md` lines 81–84.)

### Process findings and follow-ups

The F3-class read-only-sandbox launcher trap must be closed at the launcher (always `-s workspace-write` with a writable `TMPDIR`); the stale `.claude/worktrees/cs-pedagogy-ai-cf3aed` worktree breaks `codex-run-v3` strict-scope launches through nested-repo refusal and remains an open audit item wanting a decision; and pattern-based `pkill` must never be used on this shared machine — one such kill terminated a sibling's suite run. Council-log edits need the gated site-lane tests before landing. (Evidence: `RUN_STATE.md` lines 103–110; `966dd39`.)

**Follow-ups:** confirm `d117-production-proof` green at `e871f5b`; lead full unpiped suite at the final head (the last full-suite evidence is `8038ccd` at 2,934 tests OK with 86 skips, and the four parcels since are focused-verified only); D-121 terminal review; merge, which lifts the mint bar. Then the bench block — kernel-gate clear-back of both `test_gen_state` pins, removal of Ed's temporary history-rewrite and `gh release` rules from `.claude/settings.local.json`, and the deferred-with-record PR ledger items. Then FLOOR-COMMONMODE-01's full audit and D-118 gauntlet, rebase and land, the Ed-funded p256 floor cells, WO-3, pack regeneration and freeze. (Evidence: `RUN_STATE.md` lines 81–101; `trust-fullsuite-8038ccd.log` lines 115/117.)

**Yield/spend:** no runner census or summable token record exists for this session, so whole-session spend and an exhaustive launch count are **UNVERIFIED**. Recorded wall clocks: the `8038ccd` full suite 14,412 s; the round-2 Sol full discovery 1,575 s; the guard-fix Sol full suite 1,604 s; `test_run_campaign` 138.7 s and 136.4 s; each flake-loop iteration 379.6–384.1 s.

**Source cautions:** `RUN_STATE.md` line 54 records a peak of about nine concurrent streams while D-129 clause 1, minted the same session, says about eight — the exact peak is **UNVERIFIED**. The checkpoint groups the trust parcels topically; branch order is `99d0e9b` → `e807d5f` → `f588f86` → `e871f5b`, so the guard hardening landed between the two custody rounds. The decisive CI outcome at `e871f5b` is unresolved in this record, and PR #122 was still open at drafting; PR #124's merge (`0e2d656`, 2026-08-10) happened after the session. The sweep ran without GitHub API access and took PR states from lead-supplied ground truth. Two delegated full-suite runs died externally — a SIGTERM/exit-143 in `wo2-report2.md` and a seven-minute silent interruption inside `test_calibration_exits` in `fcm01-report.md`; attributing the first to the recorded `pkill` incident and the second to that test's normal ~380 s runtime are **inferences, not verified facts**. `sol-diag1.md` F3 discloses that the mandated `.diag-tmp` hydration destination conflicted with the hydrator's outside-repository policy and that only that destination check was overridden. The “12 stale worktrees pruned” count and the “three Sol rounds burned by the launcher trap” attribution rest on `RUN_STATE.md` alone.

## C-055: T4 — the mint bar lifts on a re-seated venue, and the freeze long pole freezes (2026-08-10/11)

Session: Fable magistrate, recorded artifacts spanning 2026-08-10 14:09 → 20:54 PT (2026-08-10T21:09Z → 2026-08-11T03:54Z), under Ed's standing 24h+ grind order. Lanes: the trust merge in the `trustverify` worktree (decisive local execution, full suite, cold-gate packet, ruling, merge, post-merge batch); the FLOOR-COMMONMODE-01 gauntlet in the `fcm` worktree (two refuters, four fix rounds, four delta audits, one escalation consult, three cold-gate sittings); the paper Rivoire-bar program in the `papered` worktree (two Sol lens runs, two dictated lens packets, five edit trains, one Opus figure lane); WO-3 to PR #125; and the arm-packet assembly plus bench bookkeeping at the desk. No stream census exists, so peak concurrency is **UNVERIFIED**. Full records: `docs/run_reports/2026-08-10-t4-window-session.md`; `docs/evidence/d117-v2-decisive-20260811/`; the custody set `~/JouleWise-window-custody/t4-session-20260810/`; commits `0e2d656`, `524a0ed`, `e74cc4c`, `4d3e3ad`, `51bcf77`, `ae6af48`, `654c53d`, `b04c5bf`, `2999f26`; the frozen branch `e9621c3`, `bbf7bdd`, `df42bcd`, `ed8715b`, `db3e212`, `123e8a5`; the paper branch `ff5fa76`…`8ac9693`.

**What shipped and what did not.** **The mint bar lifted**: PR #122 merged at `ae6af48`, head `e871f5b` exactly. WO-2 (#124) and WO-3 (#125) merged, discharging two freeze-plan work orders. D-130 was minted with its post-merge batch; the state kernel cleared back to ungated. The paper program opened as PR #126. Not shipped: FLOOR-COMMONMODE-01 is **FROZEN** with an Ed-only relicense, so pack freeze remains barred by freeze-plan Q7; PR #126 is unmerged; the mandated Python 3.11 decisive replay was still running at the checkpoint. No measurement, arming, or claim publication occurred. (Evidence: `RUN_STATE.md` lines 52–116; `FREEZE-FCM01.md`.)

### The trust cold gate: substance over venue, fenced

The `d117-production-proof` job was cancelled twice at head `e871f5b` at exactly the 360-minute GitHub-hosted cap (2026-08-10T04:33:06Z→10:33:25Z; 21:15:41Z→2026-08-11T03:16:02Z; run `31355841745`), and that cap is not raisable. Two same-signature failures fire the standing escalation trigger, and re-designating decisive authority is independently a mandatory cold-gate trigger. A cold Fable instance ruled on a mechanically-assembled packet of nine facts and three dispositions: re-designate (a), restructure first (b), or a third rerun (c) — "not supported by any evidence; listed for completeness." The ruling was (a). Decisive authority was re-seated to the lead local execution at `e871f5b` (2026-08-10T21:16:58Z→2026-08-11T00:52:37Z, rc=0, `Ran 1 test in 12938.543s`, the workflow's exact decisive test, hydrated the CI way from the anonymously-downloaded release asset with the archive digest independently re-hashed by the gate), taken **together with** the CI-proven hosted transport/authentication chain. (Evidence: `trust-coldgate-packet.md`; PR #122 comments 03:40:03Z/03:40:04Z; `docs/evidence/d117-v2-decisive-20260811/`.)

The paired contract-lens refuter concurred with (a), dissented explicitly from (b), and ruled (c) trigger-forbidden — and supplied the finding that makes the ruling defensible rather than merely convenient. Attacking the local run's hermeticity, it found the attack failing in the opposite direction: the committed ledger's 38 custody locators are absolute paths under Ed's iCloud backup tree — **the exact T2 leakage paths** — and they still exist on the executing machine with their full five-artifact layout. 38 × 5 = **190 live forbidden paths**, any one authenticated read of which fails the run. Its words: "on a GitHub runner those paths do not exist, so the assertion there is near-vacuous; on Ed's machine it is the only thing between a leak and a silent green." Two further locks were verified in branch code — a store-content lock (manifest projection equality plus governed-member hash equality, no symlinks) and a skip lock (an unset store variable can only skip or hard-fail, so "the env var being set to a populated store is inferable from the log itself, not from the operator's word"). It then refused to overclaim, recording three residual holes including "It is an unregistered-read detector, not an out-of-root detector. Do not cite it as hermeticity evidence," and disclosing that it had not re-executed the 3h35m run — which is why its condition C1 (reproducible-execution custody, not just the log) exists. It also found `main` unprotected, so the tracked docs calling the job "required" carry "a prose norm with no mechanical backstop." (Evidence: D-130 body; PR #122 ruling comment.)

Conditions C1–C6 were executed before or with the merge, not promised: the evidence bundle posted pre-merge and committed with a durable custody copy; `scripts/replay_d117_decisive.sh` landed as the one-command replay recipe with an interpreter hook; a 3.11 replay launched post-merge; WO-CI-RESTRUCTURE registered with a named-event deadline; the PR ledger, RUN_STATE and both tracked "required"-wording contract sentences amended; and D-130 minted so the fence binds future sessions. The refuter's preferred Route A — de-triggering the always-firing workflow in code — was applied **post-merge** so the merged head stayed `e871f5b` under the ruling's own condition 2. D-130 is narrow by construction: no general local-decisive lane, a five-part test for any future substitution, expiry at WO-CI-RESTRUCTURE closure, and a citation discipline ("lead-verified locally (custodied bundle) + CI-verified transport/authentication chain", never "CI-proven decisive run"). Its deadline is a **recorded deviation** from the refuter's tighter before-FCM-01 ordering, with the reasoning written into the decision rather than silently adopted. The lesson bound forward: "a decisive job whose runtime was never bounded against its venue's hard cap is a design defect." (Evidence: `654c53d`; `docs/decision_log.md` D-130; `TASK_QUEUE.md` WO-CI-RESTRUCTURE.)

### FLOOR-COMMONMODE-01: freezing as a result, not a failure to finish

Five distinct understatement mechanisms fell out of four fix rounds and four delta audits, each caught by a strictly stronger audit: omitted support-edge breakpoints (0.25 J, gauntlet); separable composition under window collapse (1.06 J, delta 1); the contrast-scaled enclosure defeated by cancellation at member scale (2.3e-13 J, delta 2 — the count-3 event that fired the mandatory cold gate); the zero-point `isclose` tolerance/identity conflation, **pre-existing in the original bank** (1.0e-9 J, delta 3); and the terminal FCM-R4-01 — the supplied zero-point value is *a* sweep value, not the sweeps' true zero evaluation, so an adversarial caller can centre the excursion composition on a false zero (4.999917146975008e-10 J exact at admitted inputs, delta 4, by a **fresh** auditor who authored neither code nor oracle). The standing escalation trigger fired correctly after round 1 (consult, not round two), and the consult located the flaw inside the *registered identity* itself, returning a terminating strict-noncollapse domain design with seven proof obligations, adopted in full. Three cold-gate sittings followed; the third's final synthesis added the two conditions worth carrying forward — **oracle-authorship separation** (the refuter authored and self-validated the acceptance oracle, committed at `ed8715b` before implementation, the implementer forbidden to edit it, byte-verified untouched by the delta auditor) and **real-fixture-first** ("every oracle in rounds 0–3 was synthetic in exactly the dimension that hid the defect"). Round 4 satisfied that oracle as written and returned the lane's only fully green canonical suite (2,986 tests OK); the fresh auditor found FCM-R4-01 anyway, and the terminal condition — any admitted-input exact understatement at any magnitude freezes the unit — was honored. What is not in doubt is recorded as carefully as what failed, including the material fact for Ed: the **production path is unaffected**, because it computes the zero point itself; every round-3/round-4 defect lives on the direct-call any-admitted-input contract. Ed's options are relicense with structural zero-threading, reverse freeze-plan Q7 and re-spec both packs' comparative cells to the worst-case default (costing the funded p256 prefill contrast's claim capability), or hold. (Evidence: `FREEZE-FCM01.md`; `fcm-refA/refB/consult/delta…4/fix…4-out.md`; `ed8715b`; `db3e212`; `123e8a5`.)

### Unique catches by layer

- **Trust cold gate:** vacated a designation the project had treated as load-bearing on the ground that it was physically unsatisfiable, reversing the magistrate's own standing position that the workflow job was authoritative. (Evidence: PR #122 ruling comment.)
- **Trust paired refuter (contract lens):** the live-decoy hermeticity finding — 190 live machine-local forbidden paths making the local venue *stronger* than the hosted one on operator leakage — plus three residual holes it refused to let the record overclaim, and the unprotected-`main` observation. (Evidence: D-130 body.)
- **FCM gauntlet, two distinct lenses:** execution lens executed the 0.25 J shortfall against a 0.50 J dense-grid width with equal control cases bounding it to non-contiguous geometry; contract lens independently proved that geometry production-reachable — cumulative-float support construction, a 1e-6 s overlap-only check, and strict validation that "authenticates rather than removes this geometry." Both also refuted their own plausible hypotheses. (Evidence: `fcm-refA-out.md`; `fcm-refB-out.md`.)
- **Escalation consult:** found the flawed assumption *inside* the registered parameter identity and returned a terminating design rather than a patch. (Evidence: `fcm-consult-out.md`; `bbf7bdd`.)
- **The four delta auditors:** strictly escalating, each finding what the previous, weaker audit structurally could not — and delta 3 explaining the blindness itself: "The committed oracle always assigns `point = contrast(0,0)` and passes that same value as `delta`, so it cannot expose this route." (Evidence: `fcm-delta…4-out.md`.)
- **The Sol implementer, against the cold gate:** round 3 returned `needs_ruling` on the gate's own dictated acceptance bar, algebraically inconsistent and failing 61 of 64 exact cases; the magistrate ruled the slip its own ("the cold gate's wording and the magistrate's transcription both carried the slip") and adopted Sol's resolution verbatim. (Evidence: `fcm-fix3-out.md`; `fcm-fix3b-prompt.md`.)
- **The refuter-authored oracle:** its own trap discrimination proved the separation load-bearing — the refuted candidate fails 16 assertions under BAR 1 "where BAR 2 alone would ship it." (Evidence: `ed8715b`; `r4-oracle/r4_oracle_spec.md`.)
- **WO-3 refuter:** refuted three of five questions with executed probes (deleting the oracle module; a two-replay probe under varied identities) and confirmed the `+10` terminal-sequence rule as an overstated clean-path cadence — a torn-target probe produced a refusal-free finalized session with 11 rows. Both findings closed pre-merge. (Evidence: `wo3-ref-out.md`; `02fdc9c`.)
- **Paper metrology lens (L1):** three blockers, one falsified by executed counterexample (n=10: corner-widened floor 0.9 J against a 1.0 J largest member half-width), and F6 propagated out of the paper into a runbook-vs-code correction on main. (Evidence: `paper-lensL1-out.md`; `4d3e3ad`.)
- **Paper web lens (L5):** five advisor-visible S1 defects — a fabricated SPEC URL suffix and date, clock synchronization attributed to SPEC rather than MLPerf Power, "phase-appropriate token denominators" credited to a paper that never defines one, two wrong author initials, and a missing same-hardware Apple-silicon characterization paper that reports no energy. (Evidence: `paper-edittrainC-prompt.md`; `2db2c6c`.)
- **Paper terms/coherence lens (L6):** the draft forbade a summed acceptance threshold and then evaluated results against exactly that sum in later sections. (Evidence: `paper-edittrainB-prompt.md` §B4.7.)
- **Magistrate at the bench:** the final linear read caught two numbering defects that survived five lenses and five trains (figures numbered by filename rather than order of appearance; "Table 1" used for two tables); the runbook drift-allowance description was corrected to the executable arithmetic (full max, not excess, with the 0.012093166090593858 s hard refusal cap stated); and the `ci` shard-4 failure was diagnosed as a load flake (2,036 s vs ~650 s for the same module) rather than a defect. (Evidence: `8ac9693`; `4d3e3ad`; `trust-coldgate-packet.md`.)
- **Arm-packet assembly:** produced 12 recorded arming-surface discrepancies purely as a by-product of writing the packet down — two different "final readiness commands," a caffeinate contradiction where the T-0 census forbids stray keep-awake processes while the reviewed launch *is* `caffeinate`, three non-identical statements of settle ownership, and packs already encoding one answer to a question the freeze addendum records as unanswered — plus the separate finding that the U11 arm-time identity-pin projection tool does not exist. (Evidence: `arm-packet-alpha-SKELETON.md` §7, P-09/O-5.)

### Deliberation resolutions and dissent

The trust ruling resolved in favour of substance over venue, against the alternative of putting a restructure of the proof job's own semantics on the mint-bar critical path — dissented from explicitly by the refuter — and paid for the shortcut with an expiry, a substitution test, a citation discipline, and a work order whose first hosted green is the required second independent execution. The FCM-01 resolution went the other way: with a green canonical suite, an untouched refuter oracle, and four rounds of investment available as momentum, the unit froze on an understatement six orders of magnitude below the ~1 J instrument attribution limit — because the class, not the magnitude, is what the registered contract may claim. Recorded dissent: the sitting-2 refuter dissent survives only as the adopted **two-claimants invariant** ("every error source admitted into the width arithmetic carries its own budget… Neither term may be asked to cover the other"); its text is not custodied. The D-130 deadline deviation from the refuter's requested ordering is likewise recorded rather than silently adopted.

### Process findings and follow-ups

**The highest-value process finding is delta-2's dropped verdict.** Its probe carried an exact rational oracle alongside the float one and printed `"understatement_found": true` with an exact worst gap of `1.73849858127358e-13 J`; its own final summary then re-keyed the output to the float fields only, so the delivered report carries just `float_understatement_found=true`. The cold-gate packet consequently framed round 2 as possibly pure float noise, and sitting 1's dictated erratum asserted the structural component "proven EXACTLY ZERO by rational-arithmetic probes." Exact-arithmetic verdicts became the terminal criterion in rounds 3 and 4 — the criterion that froze the unit — so a verdict of the dispositive class had already been executed one round earlier and never reached the adjudicator. Delta-audit prompts must **require** exact verdicts to be printed. Also recorded: two writers in one worktree (the magistrate committed the figures into the paper worktree mid-run, producing an exit-77 scope violation attributed to the agent — a false positive on the agent and a real rule violation by the lead); inline `codex-run-v3` prompts omitting the literal `WRITE_SCOPE` line fail at the launcher, logged as the fifth recurrence, prompt-file rule now standing; linked-worktree git metadata sits outside the writable sandbox, so every delegated round leaves work unstaged for lead-side commit by design; and `tests/test_calibration_exits` interrupted six delegated canonical-suite runs locally (exit 130, no assertion failure) despite the T3 flake repair.

**Follow-ups:** harvest the Python 3.11 decisive replay and record it in the evidence directory (D-130/C3; a contradiction is an automatic stop signal plus cold gate); take Ed's ruling on the FCM-01 decision packet, which the freeze banner is written to be — the cold gate's licensing authority on that unit is spent; magistrate full linear read over PR #126's head, then merge; WO-CI-RESTRUCTURE before any claim publication and before the pack-freeze merge wave, carrying the full trust gauntlet; the arm-packet resolution pass, with U11 on the freeze-lane critical path; and skill-usage rows plus worktree pruning as lanes close (the `fcm` worktree holds the frozen branch — keep until Ed rules).

**Yield/spend:** no runner census or summable token record exists, so whole-session spend and an exhaustive launch count are **UNVERIFIED**. Recorded wall clocks: the decisive local run 12,938.543 s; the lead full unpiped suite 1,589.651 s (2,945 tests OK, 89 skips); the FCM round-4 canonical suite 1,520.277 s; the round-2 canonical suite 1,571 s; Sol run durations of 4,825 s (FCM fix 2), 2,083 s (delta 3), 1,291 s (delta 2), 1,023 s (delta 4), 944 s (fix 1); and 6 h 00 m of hosted-runner time burned by each of the two cancelled CI attempts.

**Source cautions:** `RUN_STATE.md` records the inline-prompt failure as "rc 64 (5th recurrence)", but no manifest in this session's scratchpad reports 64 — the observed codes are 0/65/77/79; the claim is consistent with a launcher-side rejection that writes no manifest, but the code and the count rest on `RUN_STATE.md` alone. `FREEZE-FCM01.md` says "FROZEN at `db3e212`" while the freeze commit is `123e8a5` (code head vs banner — presentation, not conflict), and the checkpoint's commit list omits the round-3 commit `df42bcd` that the cold gate declared terminal. The checkpoint says "the two cold gates' process recommendations" and then lists three clauses. **The cold-gate sittings left no custodied ruling artifacts** — for FCM-01 only the sitting-1 input packet is on disk, and the trust refuter left no file at all, so both the FCM sitting-2 dissent text and the trust refuter's C1–C7 survive only through downstream summaries: a custody gap in the highest-authority layer the process has. The primary evidence for the delta-2 drop is in the run transcript, not the report — the report showing only the float verdict *is* the finding. PR #126's body claims "~950 words of duplication removed" while the draft grew 8,435 → 10,052 words across the program and only ~324 words of removal are substantiable; commit `e9a8c05` says "L23 F1-F6" where the lens reported F1–F7 (F7 deferred to train E, not dropped) and says the coherence fix was applied "at both sites" where the train reports three. Two of the five paper lenses (L5, L6) produced no run artifacts and exist only inside the train prompts, so their execution as subagents is inferred; train C performed no web re-verification of its own. The checkpoint was written about five minutes before train E, the numbering commit, and PR #126 landed, so its paper successor order is stale on those items. The checkpoint lists "U11 tool DOES NOT EXIST" among the 12 arming discrepancies; the packet records the twelve as document-vs-document disagreements (§7 D-1…D-12) and U11 separately as a missing-artifact precondition failure (P-09, O-5).

## C-056: T4-late — the delete-don't-authenticate gate, four strictly narrower audits, and a bench fix the next delta walked around (2026-08-11)

Session: Fable magistrate, recorded artifacts spanning 2026-08-11 01:05 → 15:56 PT, continuing the T4 window after C-055 landed (`42b7a7b`) under Ed's standing grind order. Lanes: FLOOR-COMMONMODE-01 through its stop, revival and rounds 5–9 in the `fcm` worktree; the U11 identity-pin projection gauntlet in `u11impl` (PR #131); the `test_calibration_exits` reliability gauntlet at PR #127 and its `d121-127` verification worktree; the `respec/d124-withdrawn` fallback gate lane (PR #132); WO-CI-RESTRUCTURE (PR #129); paper trains F and G; and the arming-surface discrepancy pass (PR #130). Full records: the FCM branch `impl/floor-commonmode-01` (`e3a1a54`, `0b5fce8`, `3390cb7`, `e29a062`, `4f04100`); commits `ea3f325`, `8c5009c`, `31a3863`, `f0e7cf6`, `cf23608`, `e15744c`; `origin/impl/calexits-reliability` (`b383087`, `493f01e`, `71d112a`, `7c44b5e`, `1e96f96`, `96b20ae`); `impl/u11-idpin-projection` (`f4c79a9`, `52e063d`, `fa08962`, `3657f4d`, `bb17bf0`); and the scratchpad run set (43 `*-out.status` files dated 2026-08-11, 31 manifests). The desk amendment to `docs/run_reports/2026-08-10-t4-window-session.md` carries the narrative detail for the earlier half of the block.

**What shipped and what did not.** Merged: paper train F (#128, `cc37e94`) and the arming-surface discrepancy fixes with the decision-log pagination that cured the red site lane (#130, `0340f0b`). Minted on main: **D-132** (`31a3863`, stopping rules target doom loops, not converging instruments — FCM-01 REVIVED) and **D-133** (`f0e7cf6`, the FCM-01 disposition ruled by the cold gate), plus the executed D-124 stopping-rule record (`8c5009c`) and the relicense transcription (`ea3f325`). Not shipped: FCM-01 remains an unmerged desk thread with round 9 in flight; PRs #127, #129, #131 and #132 are all open; the pack freeze is unblocked only once the fallback (#132) clears its own gate. No measurement, arming, or claim publication occurred.

### FCM-01: stopped, revived, and then ruled by the cold gate

The morning executed and then revised a stopping rule. Round 5 (`e3a1a54`, Ed-relicensed at `ea3f325`) was audited by the round-5 delta, which fired the pre-committed rule: **FCM-R5-01** — the frozen dataclass's generated constructor plus a `type()`-only admission check admitted records fabricated by direct construction, `dataclasses.replace`, `object.__new__` + `__setattr__`, copy and pickle, each carrying a false zero index and understating by exactly 4.999917146975008e-10 J (2,251,762.5 ulp of S_env) while passing registration validation. The unit STOPPED at `0b5fce8`. Ed then ruled in-thread that a stop rule exists to kill doom loops, not converging instruments (**D-132**), and the unit was revived under a design that closes the class by construction: round 6 (`3390cb7`) DELETED the public registered surface and moved the estimator arithmetic inside `extract_comparative_cell`. (Evidence: `fcm-delta5-out.md` FCM-R5-01; `0b5fce8`; `docs/decision_log.md` D-132.)

The round-6 fresh delta REJECTED it anyway, on a class no earlier round had reached: **FCM6-01**, the serialization boundary. Injecting the current registration dictionary into a genuine extraction report returned `validate_d117_mint_consumption_report(...) == []`; injecting the same identity into the genuine floor artifact returned `validate_floor_artifact(...) == []` and then `authenticate_floor_artifact_bytes(...)` returned an `AuthenticatedFloorArtifact` carrying parameter sha `dea20dc0…` at forged artifact sha `8afdcb51…`. The construction-closure claim was false at a committed admission boundary; the round's own replacement forgery test only proved `build_comparative_record` strips an `object.__setattr__` mutation, which direct JSON admission bypasses. (Evidence: `fcm-delta6-out.md` FCM6-01, V2/V3.)

That verdict matched neither branch of the pre-committed decision rule (`exact_understatement_found=false`, but the claim broken), and a round 7 would have been the next round on the fabricated-record-admission class — rule 11's mandatory cold-gate trigger. The gate sat on a mechanically-assembled packet (437 lines, primary artifacts verbatim, D-132 and the round-5 stopping record as exhibits) offering (i) round 7 under a custody-closure design, (ii) merge the fallback now, or (iii) any superior hybrid. The fresh Fable adjudicator first ruled (i). The paired Opus contract-lens refuter's brief then produced the three facts that decided it, all of which the magistrate bench-verified before the revised sitting: **the pinned mint scripts contain zero estimator vocabulary**, so the tighter floor cannot reach a minted artifact this cycle under any disposition without new D-118-gated mint work; **no consumer of `estimator_registration` exists outside its two owning modules**, so the forged field is inert; and **the production claim path binds `expected_sha256` + `expected_artifact_id`**, which the delta's V3 reproduction omitted. On those facts the adjudicator withdrew its first ruling with concessions on the record — including that `exact_understatement_found=false` was a non-finding, its arithmetic lenses never having executed — and ruled the hybrid (iii): the fallback merges after its own gate shape and the freeze lane is decoupled from FCM-01; FCM-01 continues unmerged under **ALT-D120**, deleting the serialized registration vocabulary rather than authenticating it (the D-120 precedent); a full fresh delta is owed on the moved arithmetic with permanent-drop terminality; and re-spec back to the tighter estimator only if three named items land before the freeze wave. **D-133** records it, registers WO-MINT-ESTIMATOR-VOCAB, surfaces the `425f75f` ungated-bank audit debt, and flags the schedule call to Ed rather than ruling it. (Evidence: `fcm-coldgate-packet.md`; `docs/decision_log.md` D-133; `f0e7cf6`; `TASK_QUEUE.md:201`.)

### Rounds 7–9: each audit reaching a class the previous one structurally could not

Round 7 (`e29a062`) executed ALT-D120 — `CellReport.as_row` stops emitting `estimator_registration`, the key leaves `_D117_MINT_FLOOR_OPTIONAL_KEYS` and `_CMP_OPTIONAL_KEYS`, the self-equality branch is deleted — so both of the round-6 delta's executed forgeries die as closed-profile unknown-key refusals, and the false round-6 provenance claim was corrected to what the design actually enforces with a sixth parameter-sha rotation. The magistrate stash-proved at the bench that the pre-fix code accepted the artifact forgery, and verified the refuter-authored oracle byte-untouched (zero diff lines).

The owed **O3 full delta** then cleared the arithmetic terminally: an independent Fraction campaign accepted 4,096 cases with **zero exact understatements** (minimum width margin 6.46e-27 J, minimum floor margin 5.28e-11 J), a 1,536-case old-public-surface/current-internal-seam differential matched digest `149ce12d…`, and five relocated arithmetic helpers were AST-identical after docstring removal. It found the vocabulary still admissible one level down: **FCM7-01** — the D117 profile accepted exact `estimator_registration` dictionaries at **13 nested mapping paths** including `governance.estimator_registration`, and the artifact authenticator accepted raw JSON carrying a forged registration in the first of two **duplicate comparative keys**, because `json.loads` keeps only the last while authentication binds the raw bytes. Round 8 (`4f04100`) closed both gaps — recursive refusal of the literal key at any depth in both validators, and a duplicate-key-refusing `object_pairs_hook` at byte admission — with the canonical suite finally captured at 3,018 tests OK (93 skips) and the A5 replay exact at 1.8695016260131627 on both interpreters. (Evidence: `fcm-fulldelta-out.md` V1/V2 and FCM7-01; `e29a062` and `4f04100` messages.)

The round-8 focused delta went narrower again: **F1**, duplicate-key *extraction reports* still bypass the new recursive check through a plain-`json` legacy loader (`scripts/mint_floor_artifact.py:203,1078`; `scripts/mint_floor_artifact_generalized.py:2270,3452`) — the bound raw bytes contained `estimator_registration` while last-key-wins parsing erased it and the validator returned `[]`. Round 9 launched with a mandatory loads census as a first-class deliverable, and the census is what fired: it closed F1 in scope and returned NEEDS_SCOPE naming `joulewise/analysis_engine/inputs.py` and `joulewise/analysis_engine/registry.py`, enumerating a dozen further unguarded byte-admission sites where digest binding alone does not prevent shadowed-key collapse. Round 9 was still running at drafting. (Evidence: `fcm-delta8-out.md` F1; `fcm-fix9-out.md` summary, flag and census listing; `fcm-fix9-out.status` = `RUNNING`.)

### U11: a settled design, a one-line bench fix, and the delta that walked around it

The identity-pin projection tool — the arm-critical precondition the T4 arm packet recorded as not existing — ran a four-round gauntlet in the day's second half. Its first delta REJECTED fix round 1 with three executed blockers (recorded in the T4 run report), and rule 11's same-signature trigger routed the next spend to adjudication: the magistrate settled the design (R2-A semantic supersession, R2-B no Git re-derivation on refusal paths, R2-C the projector adopts the mint's anchor implementation unmodified) and round 2 landed against it (`fa08962`). The delta on that round REJECTED again with **U11-R2-01**: freeze formats the next receipt number at minimum width, so `9999 + 1` becomes `projection-10000.json`, while successor discovery matched exactly four digits — the auditor seeded 9999, froze through the public API, committed the authenticated `projection-10000.json` successor binding the predecessor's pack ID and receipt digest, and `verify_frozen_projection(predecessor)` returned **PASS**. The magistrate fixed it at the bench in one line (`3657f4d`, `[0-9]{4}` → `[0-9]{4,}`, plus a 43-line regression proved biting in both directions).

The next delta walked around that fix: **U11-R3-01** — a committed successor with valid JSON, an active plan-tree binding and an authenticated predecessor binding, relocated to `projection-000a.json`, is silently excluded by the positive discovery allowlist *before* validation, and the predecessor PASSes again. Its V1 confirms the five-digit regression itself still passing; the defect is the allowlist shape, not the width. Bench round 4 (`bb17bf0`) made the receipts namespace governed — non-conforming committed entries refuse rather than hide a successor — and the fourth delta returned **ACCEPT** with no findings, every requested bypass (nested path, case-varied prefix and extension, full-width Unicode digits, trailing space, malformed payload, directory-shaped receipt, forged sidecar) refusing correctly. PR #131 is open. (Evidence: `u11-delta2-out.md`; `3657f4d`; `u11-delta3-out.md`; `bb17bf0`; `u11-delta4-out.md` V1.)

### Rule 1 again: hosted green, lead-verified red

PR #127 reached full hosted green — every check in the rollup SUCCESS, both `calibration-exits-exclusive` jobs included — and the magistrate's own live verification at that head failed twice with `KeyError: 'code'`. Root cause at the bench: abort-class witness cases deliberately strand their `fake_sampler.py` child (that IS the defect class under test) and the harness never reaps the strays, so roughly **24 orphaned fake samplers** accumulated across three suite runs, one alive for hours; the writer's detect-only post-teardown census then emits its JSON event *after* the refusal event, and `_json_payload()` takes the last JSON line, so the census displaces the refusal payload. CI passes only because a fresh runner's census is empty — the green was environment-masked. Fix round 3 (`1e96f96`) made the harness reap its own strays, made payload selection semantic rather than positional, and added a decoy-stray regression demonstrated failing pre-fix. The independent round-3 audit then found the class one level out: **FIND-1**, writer ownership dies with the test interpreter. Killing the owning interpreter (PID 65328) mid-case left the validator (PID/PGID 65361) alive with `--session-id session-writer-correction`, and the fresh zero-survivor guards still passed with that ambient writer present. It was not elevated to blocker — each writer has a unique witness root and ledger and the repaired selector excludes the census event, so no cross-case corruption was reproduced — and was appended to WO-SAMPLER-SUPERVISOR at `96b20ae` with its closure-regression requirement. (Evidence: `calexits-fix3-prompt.md` root-cause section; `calexits-audit3-out.md` FIND-1, V1 `Ran 26 tests in 311.839s` with an empty post-suite census; `1e96f96`; `96b20ae`.)

### Unique catches by layer

- **Round-6 fresh delta (surface-closure lens):** the serialization boundary — a class no prior round reached — proving the "closes by construction" claim false at committed validators and at the unbound authenticator, with both forgeries executed rather than argued. (Evidence: `fcm-delta6-out.md` V2/V3.)
- **Cold-gate paired Opus refuter:** every decisive input to the ruling came from the refuter's brief — the three facts (mint vocabulary absent, forged field consumer-inert, `expected_sha256` omitted from the delta's reproduction), the ALT-D120 alternative, and the hybrid that decoupled the freeze lane from FCM-01 — and they were strong enough to make a fresh adjudicator withdraw its own first ruling. (Evidence: `docs/decision_log.md` D-133; `f0e7cf6`; `fcm-alt-d120-prompt.md` header.)
- **Cold-gate Fable adjudicator:** revised on the record rather than defending the first sitting, and conceded that the delta's `exact_understatement_found=false` was a non-finding because its arithmetic lenses never ran — a concession the delta's own blocking flag G1 supports. (Evidence: D-133; `fcm-delta6-out.md` flag G1.)
- **The O3 full delta:** cleared the arithmetic terminally (4,096 exact-rational cases, zero understatements; 1,536-case differential digest match) *and* still found FCM7-01's nested-depth and duplicate-key admissions — the layer that both closed a question and opened a narrower one in the same run. (Evidence: `fcm-fulldelta-out.md`.)
- **The round-8 focused delta:** narrower still — the same duplicate-key attack surviving through a *legacy* plain-`json` loader that the new recursive check never sees. (Evidence: `fcm-delta8-out.md` F1.)
- **The round-9 mandatory loads census:** a deliverable, not an audit, that nevertheless found the widest remaining exposure by enumeration and returned NEEDS_SCOPE on two analysis-engine modules instead of silently working around them. (Evidence: `fcm-fix9-out.md` flag and census.)
- **U11 delta on the settled-design round:** executed a full public-API bypass of R2-A using a receipt number the projector itself generates. (Evidence: `u11-delta2-out.md` U11-R2-01.)
- **U11 delta on the magistrate's bench fix:** the highest-value layer justification of the day — the one-line widening was correct and its regression bites, and the very next delta walked around it with a non-numeric filename, showing that a fix authored at the bench is not exempt from the delta layer. (Evidence: `u11-delta3-out.md` U11-R3-01 with V1 confirming the prior regression green; `3657f4d`.)
- **U11 fourth delta:** caught nothing, ACCEPT — recorded because a clean adversarial round against an eight-shape-plus bypass matrix is the evidence the previous three catches were converging. (Evidence: `u11-delta4-out.md`.)
- **Lead-side live verification (rule 1):** a census/payload defect that full hosted green could not see, because the defect requires a machine with accumulated state; CI's cleanliness was the thing hiding it. (Evidence: `calexits-fix3-prompt.md`.)
- **Round-3 independent audit:** the killed-interpreter writer-stranding class, reproduced by killing the owning interpreter and showing the fresh guards still pass with the orphan alive. (Evidence: `calexits-audit3-out.md` FIND-1.)
- **Fallback gate lane:** the third gate run REJECTED the fallback not on its generated packs (faithful, tests green) but on the surfaces around it — active queue, state-kernel, strategy and readiness documents still directing the withdrawn D-124 work. (Evidence: `respec-gate3-out.md` summary.)

**The pattern worth binding forward:** every layer today caught a strictly narrower, previously-unreachable class — construction claim → JSON admission → nested depth and duplicate keys → legacy loader → unguarded engine routes; and in U11, topology → receipt width → receipt namespace. The delta-audit layer earned its spend repeatedly, including against a magistrate bench fix.

### Deliberation resolutions and dissent

The cold gate resolved against its own first instinct: custody-closure (authenticate the vocabulary) was withdrawn in favour of deletion (remove the vocabulary), on the D-120 precedent and on bench-verified facts about what the mint can actually reach this cycle. The load-bearing consequence is structural rather than technical — the freeze lane was **decoupled** from FCM-01, so an unmerged desk thread can no longer gate the pack freeze, which is what the previous freeze disposition had allowed. D-133 records the same-signature escalation trigger as satisfied by resolution through the consult with a *structurally different* remedy, not by a third validator. No unresolved model-held dissent is recorded in the named sources; the adjudicator's withdrawn first ruling is on the record as concessions rather than as dissent. The one live question was referred rather than decided: whether the gamma-arm claim capability must ship in the main paper this cycle is flagged to Ed as a schedule call, with the default (freeze does not wait; the tighter number banks for the ICPE version) stated in advance.

### Process findings and follow-ups

**The tooling class cost more than any defect today.** Four runs died at exactly 902 s with `error_stage=report_capture` and no report file at all — `calexits-fix3`, `calexits-fix3b`, `fcm-alt-d120`, `u11-fix2b` — and two more (`respec-gate`, `respec-gate2`) returned thin output with no manifest. The first diagnosis blamed the read-only sandbox's temp denial and the wrapper's positional prompt argument; the corrected root cause, recorded as an addendum, is `codex-run-v3`'s **default `--timeout 900`** killing sessions mid-turn so no `task_complete` and no `-o` file ever materialise, with the read-only sandbox real but secondary. Both rules are now in the skill-usage log: every substantive Sol run passes an explicit `--timeout` (10800 for audits and implementation), and anything that executes a suite launches `-s workspace-write` with an END-clean worktree instruction; a custom `TMPDIR` is never the fix. Three reports (`fcm-delta6`, `fcm-delta8`, `fcm-fulldelta`) exist only because they were recovered from `~/.codex/sessions` rollouts after a null final message, and carry no manifest. Notably, the round-7 implementation commit `e29a062` was consumed with an explicit protocol note that its Sol session exited rc-65 without an envelope, and was gated only through the full fresh delta that followed. (Evidence: the 2026-08-11 manifests' `run_finished` records; `~/.claude/skills/skill-usage-log.md` 2026-08-11 T4-late rows; `e29a062` PROTOCOL NOTE.)

**Follow-ups:** land round 9 with the approved analysis-engine scope and audit it fresh (the terminality clause of D-133 clause 3 still binds — any exact understatement on that head drops the estimator permanently); clear the fallback (#132) through its own gate shape, including the surfaces `respec-gate3` rejected, since the freeze lane unblocks at that merge; take Ed's schedule call on WO-MINT-ESTIMATOR-VOCAB versus the freeze wave; PR #127 through CI and D-121 to merge, after which WO-SAMPLER-SUPERVISOR carries FIND-1 and the sudoers-migration prerequisite; U11 (#131) through its final gate as the freeze-lane arm-critical precondition; WO-CI-RESTRUCTURE (#129) before any claim publication; and mint or retire **D-131**, which the U11 implementation commit and the T4 run report both cite as an adopted contract but which does not exist in `docs/decision_log.md`.

**Yield/spend:** 43 Sol run-status files carry 2026-08-11 timestamps; 31 manifests record 34 `run_started` attempts at **18 high / 16 xhigh**, with 17 runs at rc 0, 13 at rc 65 and 2 at rc 79, and 58,439 s of aggregate recorded run time (longest single runs: `calexits-impl` 6,639 s, `calexits-fix2` 4,256 s, `calexits-fix1` 4,202 s, `u11-impl` 4,041 s, `fcm-fix8` 3,906 s). Two cold-gate agents sat (fresh Fable adjudicator + paired Opus contract-lens refuter). The dictated figure of "~14 Sol runs" is an undercount against the artifact census and the count of Opus mechanics/directors (3) is **[UNVERIFIED-BY-MECHANIC]** — no Opus-side artifacts exist on disk.

**Source cautions:** **The cold gate again left no custodied ruling artifacts** — neither the adjudicator's rulings nor the Opus refuter's brief exists as a file, so the attribution of the three decisive facts, ALT-D120 and the hybrid to the refuter layer rests on D-133's prose, the `f0e7cf6` commit message and the round-7 prompt header, not on the refuter's own words; this is the same custody gap C-055 flagged in the highest-authority layer, now recurring **[UNVERIFIED-BY-MECHANIC]** as to origination. Worse, `fcm-coldgate-packet.md` was overwritten in place at 12:48 for this gate, so the T4 sitting-1 packet C-055 cited at that path no longer exists. The magistrate's dictated U11 delta numbering is shifted: the three-blocker REJECT belongs to the **first** delta (already recorded in the T4 run report), the five-digit `projection-10000.json` bypass to the **second**, and the third delta's catch is the non-numeric `projection-000a.json` name, not the five-digit number; this entry follows the artifacts. The round-9 scope approval for the two analysis-engine modules is reported by the magistrate but is not visible in the artifacts (the run was still `RUNNING` at drafting) **[UNVERIFIED-BY-MECHANIC]**. `fcm-delta6-out.md` is `completion=partial` with a blocking flag disclosing that its A5 replay, ≥500-case rational campaign, oracle mutation proof, cross-interpreter checks and canonical suite never ran — the REJECT rests solely on the executed surface-closure blocker. `fcm-fulldelta-out.md` is likewise `completion=partial` (its canonical-suite count was not captured; round 8 captured it instead), so "arithmetic cleared terminally" means no exact understatement was found by the executed campaign, not that every lens ran. The dictated "five run failures" is close but not exact against the manifests: four runs show the 902 s `report_capture` death and two more failed with no manifest at all; the skill-usage log records the class as five rc-64/65 failures across three lanes. WO-SAMPLER-SUPERVISOR is registered in `TASK_QUEUE.md` on the `impl/calexits-reliability` branch (`71d112a`), not yet on main. Local `impl/calexits-reliability` is stale at `7c44b5e`; the audited head `1e96f96` and the WO append `96b20ae` exist on `origin`.

## C-057: T5 — ten merges, the cold gate whose second reader killed the first reader's cure, and the fixture exactly as weak as the code (2026-08-11/12)

Session: Fable magistrate with an Opus lieutenant and director corps, recorded artifacts spanning **2026-08-11 ~20:35 PT → 2026-08-12 07:10+ PT**, running inside Ed's 12h autonomous window under the standing D-128 grind order and still live at drafting; the window closed at ~10:45 PT (17:45Z) on Ed's stop order, checkpoint `72b8427`. (The session is dated **2026-08-12** in the magistrate's own dictation; that is the UTC date. This entry follows the C-055/C-056 PT convention, under which the window opens on the evening of 08-11.) Lanes: the T4-late merge queue (#132, #133, #131, #127, #134, #129) executed in order under D-121 terminal review; WO-MINT-ESTIMATOR-VOCAB in `wtE-mintvocab` through a full cold gate and a two-stage attestation (PR #140); the §5C arm-readiness record generator (D-134) across `wtD-5c`, `wtD-5c-revA/-revC/-mut`, `wtD-5c-fixcode`, `wtD-5c-fixdocs`, `wtD-5c-delta` and `wtD-5c-integ`; D-135 advisory site budgets in `wtB-d135` (PR #136); the p2038 wall-clock-phase flake in `wtC-p2038flake` (PR #137); the calexits mutation-regression classifier in `wtI-calexits` (PR #139); the crash-matrix exclusive CI job in `wtF-crashmx` (PR #135); and Q8 p256 floor cells in `wtG-q8` (PR #138). Full records: main commits `dc3421f`, `b670c8f`, `b32220e`, `10578fc`, `14879e4`, `5060189`, `529188a`, `ed26a29`, `60d9e42`, `f4aa138`, `7a76a29`, `c3b2c79`, `525cc85`; the custodied cold-gate set at `docs/process_traces/2026-08-12-mintvocab-coldgate/{packet,ruling-1-original,ruling-2-refuter-brief,ruling-3-FINAL}.md`; the calexits consult trace at `docs/process_traces/2026-08-12-calexits-mutation-consult/`; the §5C chain `3a140bb` → `08f7463` → `4ff4072` → `46eb6a9` → `fc4095f` → `9abedad`/`de8148c` → `5a80e39`; and the scratchpad run set (27 manifests dated 2026-08-12, plus three reports with no manifest at all).

**What shipped and what did not.** Merged, all on 2026-08-12 UTC: **#132** (03:41Z, the D-133 O1 fallback — the freeze lane unblocks), **#133** (04:04Z, paper train G), **#131** (04:38Z, U11 identity-pin projection; D-131 flipped PROPOSED→ADOPTED on main at `14879e4`), **#127** (04:53Z, calexits reliability), **#134** (05:03Z, FCM-01 under D-133 ALT-D120), **#129** (06:51Z, WO-CI-RESTRUCTURE), **#136** (07:47Z), **#137** (07:29Z), **#139** (10:03Z) and — after this entry was drafted — **#138** (Q8 p256 floor cells; packs now 100 members/pack, quiet-window budget ratification owed to Ed at drafting). That is the T4-late queue **6/6** plus three PRs opened, gated and merged inside the same session. Minted on main: **D-136** (`f4aa138`, Ed's in-thread ruling retiring the site lane from all automatic processes — no session spends tokens on Lakebed/capsule anything, the site workflow is manual-dispatch only, and site results never gate or prompt work). Registered: WO-CRASHMATRIX-RELIABILITY (`525cc85`). Not shipped: **#135** (crash-matrix exclusive CI job) and **#140** (WO-MINT-ESTIMATOR-VOCAB, gate-complete awaiting CI) remain open at stop; the §5C integration branch `integration/5c-readiness` is assembled but unlanded. No measurement, arming, or claim publication occurred.

### The mintvocab cold gate: the first custodied gate, and the second reader who killed the first reader's cure

Rule 11's mandatory trigger fired before execution rather than after it, and — for the first time in the T-series — **the gate left its own artifacts on disk**. The packet, the original ruling, the paired refuter's brief and the final ruling are all committed at `docs/process_traces/2026-08-12-mintvocab-coldgate/` (`529188a`, custodied BEFORE execution), closing the custody gap C-055 and C-056 both flagged in the highest-authority layer.

The fresh Fable adjudicator's first ruling (`ruling-1-original.md`) authorized option A in direction and found one concrete defect: a **fail-open at the evidence-binding site**. `bind_v2_floor_artifact_evidence` (`joulewise/floor_mint_estimator.py:546-564`) swallows the binder's refusal by suffix-matching its message; because the pinned binder iterates `("absolute", "comparative")` and raises the same message for either component, *"A common-mode artifact with tampered absolute widths binds successfully. That is a refusal surface failing open."* It superseded the magistrate's five provisional conditions with ten of its own, C1–C10, and prescribed **C6** as the cure: match the refusal exactly, and only for the comparative root.

The paired Opus contract-lens refuter's brief (`ruling-2-refuter-brief.md`) then killed C6 outright. **"C6 — REFUTED. The prescribed remedy is inert; the collision is structural in v2."** Under v2 both components must carry one `evidence_root_id` (`scripts/mint_floor_artifact_generalized.py:849-854`), so *"the absolute component's message and the comparative component's message are the identical string"* — exact-and-in-full matching on the comparative root id therefore matches the absolute refusal **byte-for-byte**, and *"C6's remedy closes nothing."* The same brief found **C1 stale against a moved main**: the packet pinned `scripts/mint_floor_artifact.py` at `bf628eed…` from main `b670c8fe`, but PR #131 had merged during the sitting and `origin/main` was at `14879e4` with the file at `79229aa2…`; the refuter verified the four seam-dependent core functions byte-identical, restated the condition as C1′, and concluded *"Only C1's literal sha is stale."* It also **calibrated the adjudicator's severity down without dropping it** — *"the exposure is a defense-in-depth regression, not a directly-drivable claim forgery. It remains merge-blocking"* — weakened six further conditions, and owed four new ones.

The revised sitting (`ruling-3-FINAL.md`) ruled **option A authorized under F1–F12, all merge-gating, none advisory**, and put the layer-yield fact on the record itself: *"both prior condition sets — the provisional five and ruling-1's C1–C10 — would have certified the binding-seam fail-open as closed. The provisional set never saw it; ruling-1 saw it and prescribed an inert remedy… It was caught only because the cold pairing put a second, adversarial reader on the same primary bytes."* Ruling-3 also **rejected the refuter's own fallback** — keeping the swallow as a "minimum acceptable alternative" is *"REJECTED as a standing option"*; infeasibility of C6′ would be a fresh NEEDS_RULING to the gate, not a fallback. (Evidence: the four custodied files; `529188a`.)

### The attestation layer: a test name that claimed more than the test proved

Attestation ran as a separate, later Sol review against the fix head rather than as self-grading. It returned nine of twelve conditions met and three merge-blocking findings. The sharpest is **B1**: *"the full-CLI regression replaces the pinned binder with a stub returning an empty mapping, so it does not prove strict-bundle-derived hashes through the full mint."* The test is `test_common_mode_full_cli_path_writes_bound_exact_artifact` (`tests/test_mint_floor_artifact_generalized.py:6172-6183`) — a name asserting a binder-verified full mint over a body that stubs the binder out. The report says it plainly: *"Its name therefore overstates what it proves."* B2 caught 19 diff paths, 13 of them outside the six-path WRITE_SCOPE, against an `origin/main` that had advanced again to `30ef012`; B3 caught the canonical suites not run at the fix head.

The same run's blocking flag **G3** caught a record conflict the executing lane could not see: *"Repository lines `docs/decision_log.md:8318-8333` record the FCM delta as terminally clean, but the attestation authority explicitly directs that D-133 clause 3 be reported open."* Its `needs` is a lead reconciliation, not a patch. The dedicated B1 remediation run then landed a real full-mint proof, and the re-attestation returned `findings: []` with all four F2 sub-parts met and *"The test name accurately describes its proof."* (Evidence: `mintvocab-attest-out.md` B1/B2/B3 and flags G1/G2/G3; `mintvocab-b1-out.md`; `mintvocab-reattest-out.md`.)

### §5C: three lenses, a live forgery, and a delta that found the fix round's weaker transcriptions

The D-134 arm-readiness machinery landed as run 1-of-2 at **`3a140bb`** (base `0415f37`, PR #131's head) and went straight into three distinct lenses, each in its own disposable worktree at the same commit.

**Lens A (contract)** executed the review's central catch live rather than arguing it: **F1, blocker** — *"Generic evidence accepts operator-entered PASS, kind, digest bindings, and Boolean predicates instead of deriving domain conclusions"* (`joulewise/arm_readiness.py:802,2232`), violating derive-never-enter and D-134 clause 6. Its V2 verification ran a real reproduction and recorded `validator_status=PASS`, `operator_source=OPERATOR_ATTESTATION`, `predicate_passes=true`. The escalation to a forged **GO** is the report's own reachability claim — *"The same construction works for other generic rows and can produce GO"* — not an executed end-to-end result; the read-only sandbox is explicit that *"Write-dependent end-to-end scenarios were not recreated."* Two further blockers (uppercase Git digests accepted; receipts valid across reboot) came with it.

**Lens B (mutation)** ran a 25-mutant census against the 36-test focused suite and killed 21. The four survivors are regression gaps, each promoted to a finding: submodule mode `160000` admitted (F1), replay against a receipt-bound old pack digest (F2), duplicate numeric receipt-slot skipping (F3), and non-UTF-8 path bytes (F4, environment-dependent on APFS — the report counts only the first three as authorization-relevant).

**Lens C (operator-safety docs)** returned **seven blockers** and two clarity defects. Four are the ones worth binding forward: **F3**, a self-contradicting N/A rule (ALPHA declares `NOT_APPLICABLE` legal *only* for successor acceptance, seventy lines after calling the helper rows "not applicable on the manual route"); the dropped operator instruction *"Do not kill a running verdict, even if it takes more than two minutes"* (carried inside F6); **F1**, eleven exact status facts silently dropped from a section the branch described as preserved; and **F7**, BETA and GAMMA showing READY without the explicit non-authorizing fence, so *"A tired operator could read READY… as machine authorization to arm."* All seven were fixed as FIX-D1..D7.

The **FIX-1 delta re-audit** at `08f7463` re-derived all 35 predicate rows against the consult contract and found **33 FAITHFUL, 2 WEAKER, 0 STRONGER, 0 WRONG**. Both weaker rows sit where a contract row mixes a frozen pack fact with a live T-0 fact: `t0.ledger_reservation` (F1) required only a well-formed lowercase digest where the contract requires the receipt to *bind* this pack's plan SHA, so a receipt reserved against a different plan passed; `t0.single_launch_capability` (F2) admitted PACK-sourced evidence for two components — session/attempt IDs unused, an atomic capability available — that *"frozen bytes do not prove"*. (Evidence: `out-5c-lensA.md` F1/V2; `out-5c-lensB.md` mutation-kill table; `out-5c-lensC.md` F1–F9; `out-5c-delta.md` A1 census and F1/F2.)

### The fixture exactly as weak as the code

The bench repair of those two rows produced the day's most transferable finding, recorded in `4ff4072`: *"applying F1 immediately failed nine end-to-end and integration tests with `readiness_ledger_preflight_refused`. The fixtures had been minting reservation receipts bound to nothing — they passed only because the code was exactly as weak as the fixture."* The corpus was repaired rather than the assertion: `install_passing_evidence` now derives the bound plan SHA through the production `_pack_identity` helper, so a fixture/production divergence fails loudly instead of hiding. A magistrate-requested sentinel audit then bounded the blast radius honestly — `_LOWER_SHA256_CONTENT` has exactly **one** use site as a content requirement, not three — and seven further producer-asserted comparison booleans were **registered, not built**, under D-120's declared limitation, with the forward rule that *"a producer must PERFORM the comparison it asserts, never assert that it performed one."*

**D-132 was applied as a live instrument, not a slogan.** The magistrate ruled the occurrence count stays at **TWO**: *"The fixture weakness is the same two defects' shadow, not a new site. A THIRD occurrence is any NEW row or site found weaker-than-contract from here forward."* Converging instrument, not doom loop — with the guard armed and named in advance rather than reconstructed afterwards. The same commit message discloses that the canonical suite *"was NOT completed in the lieutenant's shell — the run was killed mid-suite by the shell cap"* and books it as owed to rule-1 magistrate verification.

### The integration tree caught what no branch could

Three §5C branches (`fix/5c-code`, `impl/5c-readiness-records`, `fix/5c-docs`) merged into `integration/5c-readiness`, and the union check found a defect that is **structurally invisible from any single branch**: the doctrine branch minted a decision entry as **D-136** — arm-readiness v1 monotonic expiry bound to the boot session — while main had minted a *different* D-136 (the site-lane retirement, `f4aa138`) after the stream's base at `0415f37`. `5a80e39` renumbers it to D-137 and states the general hazard for the record: *"a branch cannot mint a globally unique identifier from a stale base, and no in-branch check can catch it — the doctrine session's 'exactly one D-136' proof was correct on its"* own tree. The renumbering was verified in both directions (main and `origin/main` both top out at D-136; D-137 unused; after: exactly one D-137 body, one index row, zero D-136 bodies on the branch, a two-line diff, main's D-136 untouched).

### Unique catches by layer

- **Cold-gate paired Opus refuter:** the entry's headline. It proved the adjudicator's own prescribed cure **inert** on a structural fact about v2 (`evidence_root_id` single-producer-root ⇒ byte-identical refusal strings), and caught C1 pinned to a main that moved *during the sitting* (`bf628eed…` → `79229aa2…`). Neither is reachable by a single reader of the packet. (Evidence: `ruling-2-refuter-brief.md` C6/C1.)
- **Cold-gate Fable adjudicator:** found the binding-seam fail-open that the magistrate's five provisional conditions never saw, and stated on its own record that merging under those five would have shipped it. (Evidence: `ruling-1-original.md` Q1, C6.)
- **The pairing itself:** ruling-3 records that *neither* prior condition set would have caught the defect as actually closed — the first case in the T-series where the gate's own final ruling attributes the catch to the pairing rather than to either reader. (Evidence: `ruling-3-FINAL.md`, Record section.)
- **Attestation as a separate layer:** a test whose *name* claimed a binder-verified full mint over a stubbed binder (B1) — a class no implementation report will self-report — plus a stale-record/authority conflict (G3) that required lead reconciliation rather than a patch. (Evidence: `mintvocab-attest-out.md`.)
- **§5C lens A (contract):** a live derive-never-enter forgery — operator-attested evidence producing a PASS predicate, reproduced in-process. (Evidence: `out-5c-lensA.md` F1/V2.)
- **§5C lens C (operator-safety docs):** seven blockers no code lens looks for, including a rule that contradicts itself seventy lines later and eleven status facts dropped from a section described as preserved. (Evidence: `out-5c-lensC.md`.)
- **§5C lens B (mutation census):** 21/25 killed; the value is the 4 that survived, each converted into a named regression gap rather than a summary line. (Evidence: `out-5c-lensB.md` mutation-kill table.)
- **FIX-1 delta re-audit:** 2 of 35 transcriptions weaker than contract *in the fix round* — the fix-rounds-introduce-defects doctrine holding again — and both on rows mixing live and frozen modality, now the identified high-risk transcription class. (Evidence: `out-5c-delta.md`.)
- **The bench repair (magistrate):** nine fixtures exposed as exactly as weak as the code they were meant to constrain; repaired at the corpus, with the blast radius corrected downward (1 site, not 3) rather than upward. (Evidence: `4ff4072`.)
- **The integration tree:** the D-136 collision, provably unreachable from any branch. (Evidence: `5a80e39`.)
- **Direction layer (the directors' own):** an unfilled `>>> [LEAD FILLS THIS SLOT BEFORE LAUNCH]` in the doctrine-fix prompt returned `implementation: partial / acceptance: needs_ruling` on FIX-E3 rather than inventing shipped behavior — fail-closed under-specification working as designed, discharged by a 189 s follow-up run once the ruling existed. Requiring exact `file:line` from every lens converted doctrine triage into grep and surfaced **two FIX-E targets labelled MISSED**. The docs branch asserted machine behavior — *"If the Mac reboots between freeze and arm, verification automatically rejects receipts from the earlier boot session"* — from a run that finished before `08f7463`, the commit that closes the reboot gap, was committed. (Evidence: `prompt-5c-fixdoctrine.md:89,195`; `out-5c-fixdoctrine.md` verdict; `out-5c-fixdoctrine-e3.md`; `out-5c-fixdocs.md` FIX-D5 vs `08f7463`.)

**The pattern worth binding forward:** every high-yield catch this session came from a *second reader of the same bytes* — the refuter over the adjudicator's cure, attestation over the implementer's report, the delta over the fix round, the integration tree over three green branches, and the magistrate's bench over the delta's own repair. None of them needed new information; they needed a different seat.

### Deliberation resolutions and dissent

The cold gate resolved against its own first ruling on the merits: C6 was replaced by C6′, C1 by C1′, six conditions repaired and four added, and the final condition set F1–F12 was declared self-contained so that nothing in the earlier sets survives by implication. The refuter's proposed fallback (keep the swallow if C6′ proves infeasible) was **rejected as a standing option** — a live disagreement between refuter and adjudicator, resolved by the adjudicator and recorded, with the escape hatch converted into a fresh NEEDS_RULING obligation. On D-132, the magistrate ruled the fixture weakness a *shadow* of the two known defects rather than a third occurrence, keeping the escalation guard armed at two rather than letting it reset — the conservative reading of its own stopping rule. The gamma-arm premise shift (D-133 cl.4's re-spec-back conditional may fire on its own ruled terms because the session is executing faster than the freeze lane) was **flagged to Ed, not decided** — no reinterpretation was made.

### Process findings and follow-ups

**The ~60-minute subagent-shell kill cap was the session's dominant tooling loss.** Four Sol runs launched from subagent shells died with a `run_started` and no `run_finished`, at **59.8, 59.9, 59.8 and 60.0 minutes**: `out-5c-impl` (04:07:56Z, last write 05:07:46Z), `out-5c-impl-r2` (05:10:44Z → 06:10:35Z), `mintvocab-fix` (05:54:57Z → 06:54:47Z) and `mintvocab-fix2` (06:58:53Z → 07:58:52Z). Two left `*-PARTIAL-killed.patch` salvage; their `.status` files are frozen at `RUNNING`, so **status files are not evidence of a live run**. The operating rule adopted mid-session — that any run expected to exceed ~45 minutes launches from the magistrate's own shell rather than a subagent's, with the director holding itself to a ~20-minute envelope — is recorded here from the magistrate's dictation and has no artifact of its own **[UNVERIFIED-BY-MECHANIC]**. The same cap is what truncated the canonical suite in `4ff4072`.

**Envelope and sandbox classes.** Three runs returned `ACCEPTANCE_FAILED` at rc 65: `out/deltaB-d135` and `out/reviewG-q8` with `report_parse=invalid` and `semantic_status=unknown/completion=unknown`, and `out/implB-d135` with a *valid* parse but `completion=partial`. `out-5c-lensC.status` likewise records `unknown/unknown` while the report's own JSON says `findings/complete` — any tooling that trusts the `.status` file misreads lens C, and the shared signature is the verdict/findings shape rather than the model's work. One run returned rc 79 `NEEDS_SCOPE` (`mintvocab-out` attempt 1, 910 s); the approved scope expansion produced a **fresh `run_started` attempt 2**, not a resume — the first 910 s were spent again from scratch (attempt 2: 5,090 s, rc 0).

**Follow-ups:** land #140 under F1–F12 with the re-attestation on the record; reconcile G3 (the decision-log FCM entry vs D-133 cl.3's open status) as a lead ruling; take Ed's call on the gamma-arm premise shift before the freeze wave; land `integration/5c-readiness` with the D-137 renumbering intact and the magistrate's owed rule-1 canonical-suite verification at `4ff4072`'s head; #135 and its WO-CRASHMATRIX-RELIABILITY successor; #138's Q8 quiet-window budget ratification (p256 = 50 NEW bundles/pack); and the live sudo/powermetrics checklist before relying on #127's production sampler commit at arm time.

**Yield/spend:** 27 `codex-run-v3` manifests carry 2026-08-12 timestamps, recording **28 `run_started` attempts at 18 xhigh / 10 high** and 24 `run_finished` records: **20 at rc 0, 3 at rc 65 (`ACCEPTANCE_FAILED`), 1 at rc 79 (`NEEDS_SCOPE`)**, with **4 attempts leaving no `run_finished` at all** (the 60-minute kills). Aggregate recorded run time **48,512 s**; longest single runs `out-5c-doctrine` 5,764 s, `mintvocab-out` (attempt 2) 5,090 s, `out-5c-impl-r3` 4,892 s, `out-5c-fixcode` 4,772 s, `out/implC-flake` 3,911 s, `q8-out2` 3,081 s. Two cold-gate agents sat (fresh Fable adjudicator + paired Opus contract-lens refuter), plus an Opus director corps whose spend leaves no on-disk artifact **[UNVERIFIED-BY-MECHANIC]**.

**Source cautions:** **Three Sol reports exist with no manifest at all** — `out-5c-lensA.md`, `out-5c-lensC.md` and `out-5c-delta.md` have `.md` and `.status` but no `*.manifest.jsonl`, so the 27-manifest census **undercounts** the session's Sol runs by at least three, and the effort/rc distribution above covers only the manifested set. The forged-**GO** escalation in lens A's F1 is the report's stated reachability, not an executed result; the executed reproduction ends at a PASS predicate. Lens C's "4 of 7 verified" is **not** an artifact fact — lens C contains exactly one verification entry (a clean-tree `git diff --check`) and no per-finding verification or 4-of-7 tally; all seven were fixed as FIX-D1..D7. "Mixed live/frozen modality" is this entry's language, not the delta's: the delta never uses the term, it holds squarely for F2, and for F1 the *contract row* is mixed while the reported defect is a missing equality check. The magistrate's dictated "byte-identical refusal strings" describes identity **between the absolute and comparative components**, not between pre- and post-remedy strings. G3 is a blocking **flag** in the *first* attestation run (findings there are B1–B3), and its text is a decision-log-vs-authority conflict rather than staleness propagating; the nearest true staleness catches are G1 (`baseline_drift`, `origin/main` advanced to `30ef012`) and C1's stale sha. The `mintvocab-attest-out.md` counts are internally inconsistent (`not_met: 0` against a findings table marking F11(c) not met). The "asserting git state without checking, 3×" occurrence count is the magistrate's own tally and cannot be reconstructed from artifacts **[UNVERIFIED-BY-MECHANIC]**; what is verifiable is that `fix/5c-docs` carried its work uncommitted from the fix run's completion until `fc4095f` at 06:40:04 PT, seconds before the integration merge. The dictated "4 PRs opened" is an undercount: **six** PRs were opened this session (#135, #136, #137, #138, #139, #140), three of which merged the same session. `docs/process_traces/2026-08-12-mintvocab-coldgate/` is named by its UTC date; its files are dated 2026-08-11 21:54 PT.

