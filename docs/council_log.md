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
`.desk/2026-08-03-sol-debate-d108-d109.md`.

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
