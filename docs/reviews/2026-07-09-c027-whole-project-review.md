# C-027: Whole-Project Council Review (final, post-examiner)

- Date: 2026-07-09. Session shape: ideation/strategy council (shape B).
- Requested by Ed: "thorough review of the whole project in council with
  5.6 Sol Extra High" — top-level docs, scientific rigor, looping/meta
  processes, lead's discretion on lens design.
- Participants: Fable 5 lead (adjudication, verification, synthesis);
  Codex **gpt-5.6-sol, reasoning effort xhigh** (first production session
  of the new model; Codex CLI upgraded 0.143.0 → 0.144.0 to unlock it) —
  seven parallel read-only lenses + one counterreview session; one
  fresh-context Fable-tier final examiner subagent.
- Raw evidence preserved in `docs/reviews/c027/`: the seven lens reports
  (`lens-*.md`), the Sol counterreview (`counterreview.md`), and the final
  examiner report (`final-examiner.md`). The lead's draft synthesis (the
  document both examiners attacked) is superseded by THIS file; its errors
  and their corrections are recorded in §6.

## 1. Scope and declared blind spots

Seven lenses: TOPDOCS (front-facing docs), RIGOR (thesis-examiner over
methodology/claims), STATS (statistical specs vs implementation), META
(process layer), REVERSE (audit of the lead's own conduct), ARCH
(architecture/tests), NEGSPACE (what is missing entirely).

**Explicitly OUT OF SCOPE (per the final examiner — not implicitly clean):**
all lenses were static-only and single-model-family. Nobody executed
anything: the suite was not run by the council, the reduce.py energy
integrator was not numerically exercised against a real trace, live vLLM
protocol behavior was not observed, SSH/node-worker security (command
construction, host keys, injection) was not reviewed, and licensing/
redistribution of model weights and datasets in a published capstone
artifact was not reviewed. These are open review debts (queue: MET-001
scope note; security review is a named candidate for a future Codex-led
session per the security division-of-labor doctrine).

## 2. Verdict

The project's core is strong and the early rigor investment was sound:
evidence-first bundles, strict re-derivation, honest boundary labeling, a
defensible single-node adapter architecture, and a test suite that is
substantial rather than tautological. Against that, three systemic gaps:

1. **Claim-surface drift.** Reader-facing docs drifted from binding
   decisions and raw evidence (wrong token denominator, superseded
   statistics rule, contradictory next-action state, over-strong
   absolutes). Corrected this session (§4).
2. **Contracts without an engine.** The statistical claim machinery the
   docs advertise exists as specs/decisions but not as code — no
   paired/block contrast CI (D-053), no executable floor/claim gate, no
   claim evaluator, propagated variance never feeding an interval — and
   the engine had NO queue owner. The existing six real bundles are
   **legacy L1 observations under the claims ladder's manual-review
   carve-out** (D-037 binds from Slice 2M onward): they did not "fail"
   later gates, but they must be labeled legacy L1 with documented
   waivers, and no stronger claim may be built on them.
3. **The loop outran its own audit trail and the graded deliverable.**
   The D-050-mandated invocation manifest holds two smoke rows against
   ~100 claimed delegated invocations; four non-bookkeeping commits landed
   directly on main against D-031; effort tipped toward breadth (packs,
   registry, site, meta-process) while the capstone-critical path is
   starved: no captured grading rubric, no report source, backup on the
   same physical disk, no end-to-end data→figure→report slice.

## 3. Blockers (B1–B8) with per-item verification lines

Verification denominator, stated plainly: the lead verified every
blocker-class claim below by direct file/git reads (~15 checks); the Sol
counterreview independently re-checked 13 items (11 pass, 2 fails — both
were LEAD synthesis errors, corrected in §6, not lens errors); the final
examiner independently re-verified B1–B7 from the repo. Should-fix and
nit tiers were NOT systematically re-verified — their acceptance below
relies on lens citation quality, which was 100% accurate on every claim
that was checked.

- **B1 — Token-denominator mislabel.** README/PROJECT_STATUS advertised
  "~77–88 mJ per generated token"; that range is `energy_token_j`
  (prompt+output denominator). Correct output-token values: 79.40/90.46/
  90.45 mJ (mean 86.77). The 122B "~583 mJ/token" was already the correct
  output-token metric. Both headlines also paired gross request energy
  with idle-subtracted token energy without naming the basis change.
  *Verified: lead read all six `runs/*/summary_metrics.json` + README:28;
  examiner reproduced arithmetic.* → Fixed this session (living docs) +
  append-only addendum to the 2026-07-06 report.
- **B2 — Superseded statistics rule on the advisor surface.**
  PROJECT_STATUS:327 stated the marginal-CI-separation rule that D-053
  (decision_log:2606) explicitly forbids ("never marginal-interval
  separation"). *Verified: lead + examiner direct reads.* → Fixed this
  session.
- **B3 — RUN_STATE cannot yield one correct next action.** TWO defective
  blocks (adjudication amended by counterreview + examiner; the lead's
  draft wrongly called the first block "correct" — see §6): the restart
  block names P2-022/P2-023 as next [AGENT] work despite binding D-041
  post-2M sequencing (hedged parenthetically post-489b25c, but still
  ambiguous — META's finding stands); the "What Is Next" block orders
  Wave-2 ranks 0a–0d, all DONE in the queue. *Verified: lead read both
  blocks + queue row 0a; examiner re-read.* → Both blocks replaced this
  session with a single pointer; structural fix (generated state kernel)
  is DOC-008.
- **B4 — Claim machinery unimplemented and unowned.** No contrast/
  multiplicity code anywhere in `joulewise/` or `scripts/` (grep clean);
  `reduce._window_claim_eligibility` checks evidence PRESENCE, never
  magnitude vs floor/effect; `run_campaign.verdict_for` returns
  "publishable" for one strict-valid bundle; no queue row owned the
  engine. `uncertainty: null` in all six real bundles. *Verified: lead
  greps + reads of reduce.py:523/run_campaign.py:1209; examiner
  re-verified in full.* → New rows P2-037/P2-038/P2-041/P2-042; legacy
  bundles labeled legacy L1 (§2.2).
- **B5 — The mandatory invocation manifest is empty of real work.**
  Exactly two `/bin/echo` smoke rows, both `disposition: pending`,
  missing the orchestration.md:169 minimum fields, against ~35 (C-022),
  ~20 (C-024), ~60 (C-025), ~6 (C-026) claimed invocations. Recoverability
  of out-of-repo evidence (codex-run observer index at
  `~/.codex/claude-spawned/index.jsonl`, workflow journals, scratchpad
  out-files) is **believed partial, unverified** — the remedy is a
  recoverability AUDIT labeling each invocation recovered / partially
  recovered / unrecoverable, never asserted recovery. *Verified: lead and
  examiner both read the manifest.* → MET-001; this session appends its
  own 10 invocation rows with archived-output paths as the first
  compliant entries. NOTE discovered during the fix: `.codex-bridge/` is
  GITIGNORED, so the manifest is local-only and cannot serve as
  repo-auditable evidence as-is — MET-001 must decide track-the-manifest
  vs snapshot-per-session into `docs/` (the C-027 rows are meanwhile
  mirrored by the tracked run report + archived lens files).
  Recoverability upside found during the same fix: the codex-run
  observer index (`~/.codex/claude-spawned/index.jsonl`) holds FINISHED
  rows WITH session ids for at least 37 historical lens/counterreview
  invocations — the MET-001 audit has a real substrate.
- **B6 — D-031 breaches: direct-to-main code commits.** `a05e54d`
  (campaign scripts + tests), `8856c04` (controller/environment + tests),
  `a835c73` (claims linter + tests inside a 26-file bookkeeping commit) —
  three code+tests commits — plus `36d5641` (33-line `build_site.py`
  behavior change, NO tests), which postdates the recorded verification
  head `c095c83`, so main carried code beyond the verification claim.
  D-031 permits only single-commit bookkeeping to bypass PR. *Verified:
  lead `git show --stat` all four; counterreview and examiner confirmed
  first-parent placement; counterreview corrected the lead's "all four
  contain code+tests" overstatement.* → MET-001 breach addendum +
  RETRO-001 independent review of the combined diffs.
- **B7 — Evidence-integrity trio (split severity per counterreview).**
  (a) IMMEDIATE, core path: a zero-length measured window reduces to a
  "successful" 0 J summary and strict validation blesses it
  (reduce.py:751; strict sampling floor conditional on positive duration)
  → P2-040, pre-Window-A. (b) GATED on NVIDIA live promotion, pins
  already provisional: vLLM SSE stream chunks counted as output tokens
  (node_worker.py:388-395; fixture hardcodes `["A","B","C"]`), and strict
  raw-lineage verification is powermetrics-only (cli.py:713) → NV-GATE-2
  acceptance gates, NOT Window-A blockers. *Verified: lead read all three
  cited regions; examiner re-verified all three.*
- **B8 — Scientific-protocol blockers (design-level, lens-evidenced).**
  (a) Legacy headline labeling obligation (reframed per counterreview —
  see §2.2). (b) Outcome-dependent repetition top-ups with ordinary 95%
  CIs (analysis_plans:102/124/146) invalidate nominal coverage → policy
  D-062 (fixed-n default + explicit demotion rule, §5-Q3). (c) Split Q1
  compares split against the observed MIN of two monolithic baselines —
  post-hoc comparator selection → SPLIT-AP row (dual predeclared
  references, win = beats both, joint adjusted intervals) folded together
  with the split-estimand freeze (NEGSPACE #7). *Verified: counterreview
  re-checked the AP top-up rows and the min() comparator definition
  directly; the legacy reframe was its own catch.*

## 4. Corrected this session (living docs only; history via addendum)

1. README + PROJECT_STATUS token claims rewritten with explicit bases:
   1.5B: ~47.2 J gross/request (≈44.4 J idle-subtracted); ~79–90 mJ per
   generated output token (idle-subtracted basis; mean 86.8); 122B:
   ~304.0 J gross (≈298.7 J idle-subtracted); ~582–585 mJ/output-token
   (idle-subtracted; mean 583.4); both labeled **legacy L1 preliminary
   observations (manual review; pre-2M)**.
2. PROJECT_STATUS "repeatable to 0.3%" → "gross-energy sample CV 0.3%
   across three sequential repetitions in one warm-cache session".
3. PROJECT_STATUS "~0.03 J prefill" → short prefill below current
   detection capability, not resolvable (D-055/registry Q-band).
4. PROJECT_STATUS marginal-CI bullet → D-053 contrast rule + three-way
   wording + floor gate.
5. "Campaign-ready" (README/PROJECT_STATUS) → "pre-campaign software
   review cleared; campaign execution remains gated on shakedown,
   calibration, quiet machine, and external backup."
6. Indefensible absolutes softened (PROJECT_STATUS "can never diverge",
   "every claim auditable"; decision-count claim de-volatilized).
7. RUN_STATE: both next-action blocks replaced by one restart pointer
   (queue is the only ordering authority; current [AGENT] state named
   honestly: at review time no row was unambiguously READY; the same
   session's queue repair then established the explicit order P2-040 ->
   P2-038 -> P2-039 -> RPT-001 -> P2-042 -> P2-037).
8. Append-only addendum to `docs/run_reports/2026-07-06-slice-2i-first-real-energy.md`
   correcting the historical table's denominator labeling.
9. Hailo `if-viable` remnants relabeled; milestones auth-gate row closed
   as of 2026-07-06; R-017 stale path fixed; RUN_STATE head-pointer
   wording fixed.
10. This session's 10 Codex invocations appended to
    `.codex-bridge/invocation_manifest.jsonl` with role/model/outcome and
    archived output paths (first D-050-compliant rows).

## 5. Council positions adopted (after bounded discussion)

- **Q1 Process restructure:** Sol's counter-proposal ADOPTED over the
  lead's draft staging — the thin machine-readable state kernel (task ID,
  lane, status, dependencies, authority, acceptance pointer, stop-card
  pointer; RUN_STATE restart block and live queue view generated from it)
  is Stage 1, not deferred; policy-doc generation comes later because
  supersession needs semantic judgment. Big-bang migration rejected by
  both sides. → DOC-008 (D-063).
- **Q2 Layer-drop rule:** two-zero-sessions rule RETIRED (falsified by
  the integration-review zero/zero/five sequence). Replacement per
  counterreview: applicability decided by PRE-DECLARED mechanical
  predicates (not post-hoc "applicable" judgment), outcome taxonomy
  separating accepted-unique-defect / duplicate / clean-verification /
  false-positive-suppression, fixed severity weights, review-after-3-
  exposures as a TRIGGER for an expected-loss decision, never automatic
  deletion; safety/final-head/integration layers are never auto-dropped
  on zero-defect streaks. → D-061.
- **Q3 Sequential sampling:** fixed-n confirmatory design is the default
  (n chosen from Window-A variance evidence BEFORE observing pack
  effects; nearer 10 than 5 for near-floor contrasts). Explicit demotion
  rule: any outcome-dependent top-up permanently demotes that contrast to
  exploratory; the original fixed-n analysis is reported regardless of
  direction; pooled estimates never presented as retaining nominal
  coverage; no re-promotion. Pre-registered two-look alpha spending is
  PERMITTED for a specifically justified expensive campaign, never the
  default. → D-062.
- **Q4 Stop line:** direction adopted, gates amended per counterreview:
  (1) rubric/calendar by a hard date, else a RECORDED provisional grading
  contract + conservative internal deadlines (external silence triggers
  scope fallback, not paralysis); (2) off-machine backup + restore proof
  is a hard gate before retaining any NEW irreplaceable evidence (does
  not block report drafting or correctness fixes); (3) the Window-A gate
  includes smoke, frozen sampling rule and guard factor, production
  uncertainty metadata, versioned floor artifact, floors, baselines, and
  an executable contrast/claim-readiness path before L2 interpretation;
  (4) vertical slice = real report skeleton + reproducible
  bundle→analysis→figure→claims-row→report-page path (legacy bundles may
  drive it, labeled legacy L1). Recorded as PROPOSED D-060 (append-only
  amendment to D-041/D-052 + risk register R-018) — **awaiting Ed's
  ratification** since it allocates Ed-facing work.
- **Governance remedies (REVERSE):** dated breach addendum naming the
  four D-031 commits; RETRO-001 independent review of their combined
  diff; PR #18 wrong-base reclassified as a merge-gate breach (C-017
  addendum); stop-card override addendum for the advisor-site episode
  (user direction existed; recording it was skipped); credential-boundary
  push procedure; where final-head review evidence is unrecoverable, the
  affected gates are marked **"reported, independently unverifiable"** —
  not silently left standing. → MET-001.

## 6. Errors in the lead's draft synthesis (recorded, not erased)

Both examiners attacked the draft; all accepted corrections:

1. Draft called RUN_STATE:91-96 "correct" — wrong; it advertises
   D-041-blocked work (counterreview spot-check FAIL; examiner concurred).
2. Draft claimed all four B6 commits "verified to contain code+tests" —
   `36d5641` has no tests (counterreview FAIL).
3. Draft said legacy bundles "failed the advertised gates" — those gates
   bind from 2M onward; correct disposition is legacy L1 + waivers.
4. Draft asserted observer-index recoverability as fact — downgraded to
   believed-partial, unverified, pending audit.
5. Draft treated the ARCH trio as undifferentiated project blockers —
   split into immediate vs NVIDIA-gated.
6. Draft's calibration note self-contradicted (immediate default-model
   promotion alongside a pending sealed A/B) — promotion removed.
7. Draft omitted the disposition table, four same-class claim-surface
   defects, PR #18, the guard-factor freeze, the production evidence
   path, and the reference-cell/evidence-date items — all restored.

Calibration honesty note: this session's only confirmed review errors
were the LEAD's (draft synthesis), not the lenses'.

## 7. Disposition table (every lens finding → ruling → owner)

Rulings: ACC=accepted, ACC-AM=accepted as amended, DUP=duplicate.
Owners: SESSION=fixed this session; queue row IDs are created this
session in TASK_QUEUE.md; MET-001 = audit/addenda batch; D-0xx =
decision entry.

| Lens # | Finding (short) | Ruling | Owner / target |
|---|---|---|---|
| TOP-1 | Token denominator + mixed basis | ACC (B1) | SESSION + 2026-07-06 addendum |
| TOP-2 | Superseded marginal-CI rule | ACC (B2) | SESSION |
| TOP-3 | RUN_STATE dual next-action | ACC (B3) | SESSION + DOC-008 |
| TOP-4 | "Campaign-ready" outruns gates | ACC | SESSION |
| TOP-5 | Stale exit-checklist rows vs D-023 | ACC | DOC-009 |
| TOP-6 | D-058 stack-identity table absent from claims | ACC | SESSION (pointer) + RPT-001 (full table) |
| TOP-7 | 170 vs 180 bundle count vs D-054 | ACC | MET-001 (D-054 amendment) |
| TOP-8 | Milestones auth gate stale | ACC | SESSION |
| TOP-9 | Decision-count overclaim | ACC | SESSION |
| TOP-10 | Indefensible absolutes | ACC | SESSION |
| TOP-11 | PROJECT_STATUS accretion | ACC | DOC-008 |
| TOP-12 | Hailo if-viable remnant | ACC | SESSION |
| RIG-1 | Denominator (dup B1) | DUP | — |
| RIG-2 | Headlines never passed advertised gates | ACC-AM (legacy L1 + waivers, not "failed") | SESSION labels + RPT-001 claims index |
| RIG-3 | No production path for gate evidence | ACC (B4/op) | P2-038 (pre-Window-A) |
| RIG-4 | Top-ups invalidate CI coverage | ACC (B8b) | D-062 + AP-EDIT |
| RIG-5 | Split min-comparator selection bias | ACC (B8c) | SPLIT-AP |
| RIG-6 | Floor transport across regimes unidentified | ACC | P2-039 |
| RIG-7 | Rail-proxy attribution + first-sample phase bound | ACC | P2-038 (empirical marker bound); L1 labeling SESSION |
| RIG-8 | "Repeatable to 0.3%" overstatement | ACC | SESSION |
| RIG-9 | Two points identify no scaling effect | ACC (premise already conceded by D-055) | SESSION prose check |
| RIG-10 | AP1 "extrapolation" mislabel | ACC | AP-EDIT |
| RIG-11 | "Not resolvable" ≠ replication success | ACC | AP-EDIT (3-outcome rule) |
| RIG-12 | Prose vs D-053/D-055 conflicts | ACC | SESSION (status doc) + contract sync in AP-EDIT |
| STA-1 | Contrast CI does not exist | ACC (B4) | P2-037 |
| STA-2 | No executable claim gate; "publishable" | ACC (B4) | P2-041 + P2-037 |
| STA-3 | Propagated variance never feeds CIs | ACC (B4) | P2-037/P2-040 |
| STA-4 | Floor math unimplemented; guard factor unfrozen | ACC | P2-039 (freeze BEFORE data) |
| STA-5 | Gross request wrongly requires drift evidence | ACC | P2-040 |
| STA-6 | One-edge interpolation bound understates 2× | ACC | P2-040 |
| STA-7 | Config token counts beat runtime-observed (D-058) | ACC | P2-040 |
| STA-8 | Zero-MAD masking; no LOO | ACC | P2-040 (fallback flag) + P2-037 (LOO) |
| STA-9 | Campaign usability ignores other ineligibility | ACC | P2-041 |
| STA-10 | No analysis grouping/contrast identity from matrix | ACC | P2-042 |
| STA-11 | Tests green against broken claim machinery | ACC | mutation-test acceptance criteria on P2-037/040/041 |
| STA-12 | Contract prose out of sync | ACC | AP-EDIT |
| MET-1 | RUN_STATE trap pointers | ACC (B3) | SESSION + DOC-008 |
| MET-2 | Catch-attribution evidence absent | ACC (B5) | MET-001 |
| MET-3 | Yield accounting has no stable taxonomy | ACC | D-061 + MET-001 |
| MET-4 | Two-zero drop rule unsound | ACC | D-061 |
| MET-5 | Playbook/orchestration/intake conflicts | ACC | DOC-008 |
| MET-6 | Backup gate inconsistently expressed | ACC | SESSION (RUN_STATE wording) + queue P0-003 rank |
| MET-7 | D-050 revisit fired, unadjudicated | ACC | MET-001 |
| MET-8 | One-fact-one-home regressed (+9.5k lines) | ACC | DOC-008 |
| MET-9 | Planning-reflection protocol is ceremony | ACC | DOC-008 (retire standalone; fold fields into queue rows) |
| MET-10 | Two live site-deploy policies | ACC | SESSION (deploy done) + MET-001 policy note |
| MET-11 | Stale head pointer; R-017 path | ACC | SESSION |
| REV-1 | Manifest empty vs D-050 | ACC (B5) | MET-001 + SESSION (own rows) |
| REV-2 | Direct-to-main D-031 breaches | ACC (B6) | MET-001 addendum + RETRO-001 |
| REV-3 | Self-merge conditions self-attested | ACC | MET-001 ("reported, independently unverifiable" markings) |
| REV-4 | PR #18 wrong-base merge | ACC | MET-001 (C-017 addendum) |
| REV-5 | Stop-card work without recorded override | ACC | MET-001 (record user direction) |
| REV-6 | Push-promptly failed at credential boundary | ACC | DOC-008 (procedure) |
| REV-7 | Consistency sweep missing/ineffective | ACC | SESSION (real sweep run) + MET-001 |
| REV-8 | Queue closures vs D-023 authority | ACC | DOC-009 |
| REV-9 | Blocked tasks advertised; P0-003 rank | ACC | SESSION (queue) |
| REV-10 | Dead follow-ups (D-013, idle corpus, dvfm, cold-load) | ACC | SESSION (shelf rows w/ triggers) |
| REV-11 | Writer-separation violation | ACC | DOC-008 (two-writer rule in-repo) |
| REV-12 | Council fix-round count ambiguity | ACC | MET-001 (clarifying addendum) |
| ARC-1 | vLLM chunk≠token | ACC-AM (NVIDIA-gated) | NV-GATE-2 |
| ARC-2 | Strict lineage powermetrics-only | ACC-AM (NVIDIA-gated) | NV-GATE-2 |
| ARC-3 | Zero-window strict-valid success | ACC (immediate) | P2-040 |
| ARC-4 | Two transport protocols; SSH hardcode | ACC | ARCH-DEBT (Phase-3 prep) |
| ARC-5 | No experiment resume; non-atomic manifest | ACC | ARCH-DEBT (document premise + atomic write in P2-040) |
| ARC-6 | Cleanup failures don't affect status | ACC | P2-040 (local) + NV-GATE-2 (remote) |
| ARC-7 | NVIDIA cooldown silently skipped (generated IDs) | ACC | NV-GATE-2 |
| ARC-8 | Unknown config keys ignored; warmup_seconds dead | ACC | P2-040 (reject-or-warn + delete/implement) |
| ARC-9 | Report ignores D-058 co-display | ACC | RPT-001 |
| ARC-10 | Contract promises split modes code lacks | ACC | AP-EDIT (mark Phase-3-future) |
| ARC-11 | Stub integration; no conformance suite | ACC | NV-GATE-2 (localhost subprocess test) |
| ARC-12 | Event-schema/clock-domain prose conflicts | ACC | AP-EDIT |
| NEG-1 | Grading contract/calendar unknown | ACC | ED-EXTERNAL P1-008 (escalated; provisional-contract fallback per D-060) |
| NEG-2 | No report source/writing runway | ACC | RPT-001 |
| NEG-3 | Backup on same disk | ACC (already P0-003) | ED-EXTERNAL rank 0 |
| NEG-4 | Compound critical-path risk unregistered | ACC | D-060/R-018 + milestones evidence-by dates |
| NEG-5 | No data→figure→report slice | ACC | RPT-001 |
| NEG-6 | No executed metrological validation | ACC | ED-EXTERNAL P1-003 meter decision (freeze limitation if no) |
| NEG-7 | Split estimand not frozen | ACC | SPLIT-AP |
| NEG-8 | Between-session/reboot reproducibility unowned | ACC | P2-015 acceptance (daily reference cell) + registry row |
| NEG-9 | Third-party repro undemonstrated | ACC | REPRO-001 (env lock + published pack + external re-reduction) |
| NEG-10 | Agent loop as schedule/scope risk | ACC | R-018 + D-060 stop line |

Counterreview attacks 1–9: all ACC (see §6). Examiner changes 1–7: all
ACC (this document is the compliance).

## 8. New-model calibration record (gpt-5.6-sol, xhigh) — batch 1

Operational: CLI 0.143.0 rejected the model ("requires a newer version");
upgraded to 0.144.0. 9 sessions total (1 smoke, 7 lenses, 1
counterreview): 9/9 OK exits, zero stalls, zero launch failures after
upgrade, wall-clock ~13–32 min per lens at xhigh.

Quality signal (adjudicated, not volume-based): every lens file:line
claim that any verifier checked (~28 distinct checks across lead,
counterreview, examiner) was accurate; two lenses corrected lead-authored
prompt premises unprompted (NEGSPACE 4, RIGOR 1); STATS supplied worked
numeric counterexamples unprompted; the counterreview caught 3 real
synthesis blockers including 2 outright lead errors and out-argued the
lead on migration staging (Q1) — the invited-judgment-out-designs-lead
pattern holding for the new model. Confirmed false positives so far:
zero among verified blocker-class claims; **lower tiers unaudited** —
FP rate there is unknown, not zero.

Doctrine consequence (per model-version scoping): this is one promising
calibration batch, NOT a promotion. The pre-registered sealed A/B (same
rubric, findings classified unique/overlap/FP with fix cost) remains the
gate before delegation-boundary expansion or default-model changes.

## 9. Deliberation trace (design-bearing exchanges only)

- **Legacy-gates framing.** Lead draft: bundles "failed the advertised
  gates." Counterreview: gates bind from 2M (D-037); applying them
  retroactively manufactures an ex-post-protocol defense problem; correct
  frame is legacy L1 + manual waivers. Resolution: counterreview
  prevailed outright — the lead's framing would have HARMED the defense
  it meant to protect. No dissent.
- **Restructure staging (Q1).** Lead draft deferred the machine-readable
  state file to stage (c) fearing mid-project migration risk.
  Counterreview: deferring the kernel leaves the demonstrated failure
  mode (two hand-maintained next-action blocks) fully active, and policy
  generation is HARDER than state generation because supersession needs
  semantic judgment — so the lead's ordering was backwards. Resolution:
  counterreview prevailed; kernel is Stage 1. No dissent.
- **ARCH severity.** Lead draft listed the trio as undifferentiated
  blockers. Counterreview: two of three are gated on provisional NVIDIA
  paths; conflating them distorts Window-A priority. Resolution: split
  adopted. Lead notes (recorded, not a dissent) that ARC-1/2 remain hard
  acceptance gates on any claim-bearing NVIDIA promotion.
- **Layer-drop rule (Q2).** Lead proposed "3 applicable sessions,
  severity-weighted." Counterreview: "applicable" and "severity-weighted"
  reintroduce post-hoc discretion — the exact unfalsifiability being
  cured; predicates and weights must be pre-declared, and evaluation
  triggers a decision rather than auto-deletion. Resolution: adopted with
  the counterreview's mechanical-predicate construction.
- **Examiner's validity-threats section** (single-family static-only
  review; lead self-adjudication asymmetry; calibration circularity) was
  accepted in full and is now a standing scope-declaration requirement
  for future council records (§1 pattern).

## 10. Follow-ups created

Queue rows (see TASK_QUEUE.md this commit): P2-037 contrast/claim engine
(pre-P2-006-interpretation gate); P2-038 production uncertainty evidence
path + shakedown assertion (pre-Window-A); P2-039 floor artifact: guard
factor frozen pre-data, ABBA delta, versioned schema, hand fixtures,
per-regime transport rule (pre-P2-015-beyond-smoke); P2-040 reducer/gate
correctness batch; P2-041 campaign verdict split; P2-042 frozen analysis
manifest; NV-GATE-2 NVIDIA live-promotion additions; DOC-008 process
architecture v2 stage 1 (state kernel); DOC-009 status-authority
reconciliation; MET-001 audit addenda + manifest recoverability audit;
RETRO-001 independent review of the four B6 diffs; RPT-001 report
skeleton + vertical slice; SPLIT-AP split estimand + dual-reference
freeze; AP-EDIT analysis-plan/contract text corrections; REPRO-001
environment lock + external re-reduction. Decisions: D-060 (PROPOSED,
awaiting Ed), D-061, D-062, D-063 (accepted). Risk: R-018 (agent-loop
schedule/scope risk).
