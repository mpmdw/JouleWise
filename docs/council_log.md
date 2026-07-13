# Council Log

Chronicle of multi-model review councils: sessions where more than one
model reviews, counterreviews, or votes on JouleWise work before it
lands. Companion to `docs/decision_log.md` (which records WHAT was
decided about the system; this file records HOW cross-model review
reached it). One entry per council session; keep entries concise —
positions, votes, resolutions, and follow-ups, not transcripts.

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
