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
