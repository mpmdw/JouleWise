# C-027 Whole-Project Council Review — LEAD SYNTHESIS (DRAFT, pre-examiner)

Session: 2026-07-09. Shape B ideation/strategy council. Peer: Codex gpt-5.6-sol
(xhigh), first production session of the new model. Seven parallel read-only
lenses (TOPDOCS, RIGOR-examiner, STATS, META-process, REVERSE-orchestration,
ARCH, NEGSPACE), lead verification of all blocker-class claims against the
repo. Lens outputs: scratchpad lens-*.md.

## Verdict (lead, draft)

The project's core is strong and the early rigor investment was sound:
evidence-first bundles, strict re-derivation, honest boundary labeling, a
defensible adapter architecture for single-node backends, and a test suite
that is substantial rather than tautological. Against that, the council found
three systemic gaps:

1. **Claim-surface drift.** Reader-facing docs have drifted from the binding
   decisions and the raw evidence: the README/PROJECT_STATUS headline
   "77-88 mJ per generated token" actually cites `energy_token_j`
   (prompt+output denominator; the true output-token range is 79.4-90.5 mJ);
   PROJECT_STATUS still states the marginal-CI-separation rule D-053
   explicitly superseded; RUN_STATE carries two contradictory next-action
   blocks (the stale one orders work the queue marks DONE).

2. **Contracts without an engine.** The statistical claim machinery that the
   docs advertise as governing claims exists as specs/decisions but not as
   code: no paired/block contrast CI (D-053), no executable floor/claim gate
   (the P2-029 "claim gates" row landed only a window-evidence precheck),
   propagated variance attached as metadata but never feeding any interval,
   and `run_campaign` calling a single strict-valid bundle "publishable."
   Crucially, the contrast/claim engine has NO queue row — an unowned
   obligation, not planned sequencing. None of the six existing real bundles
   passed the advertised gates (`uncertainty: null` in all).

3. **The loop is outrunning its own audit trail and the graded deliverable.**
   The invocation manifest D-050 made mandatory holds two smoke rows against
   ~100 claimed delegated invocations (real evidence exists in codex-run's
   observer index outside the repo, but not where the rule requires);
   multi-file code commits landed directly on main against D-031 (a05e54d,
   8856c04, a835c73, 36d5641 — the last past the recorded verification head);
   and effort has tipped toward breadth (packs, registry, site, meta-process)
   while the capstone-critical path is starved: no captured grading rubric,
   no report source, backup on the same physical disk, no end-to-end
   data→figure→report slice.

## Lead-verified blockers (all spot-checks confirmed)

- B1 Token-denominator mislabel: README.md:28, PROJECT_STATUS.md:94 vs
  runs/*/summary_metrics.json (79.40/90.46/90.45 output-token).
- B2 Superseded stats rule: PROJECT_STATUS.md:327 vs D-053
  (decision_log.md:2602 "never marginal-interval separation").
- B3 RUN_STATE dual next-action: :91-96 (correct) vs :198+ (stale Wave-2
  ordering; queue rows 0a-0d DONE).
- B4 Claim machinery unimplemented + unowned: no contrast/multiplicity code
  in joulewise/ (grep clean); reduce.py:523 precheck checks presence, not
  magnitude; run_campaign.py:1209 "publishable" after one bundle.
- B5 Manifest: .codex-bridge/invocation_manifest.jsonl = 2 pending smoke
  rows; orchestration.md:169 fields absent from bridge schema.
- B6 D-031 breaches: four cited commits verified to contain code+tests
  landed directly on main.
- B7 ARCH trio (verified at cited lines): vLLM SSE-chunk-as-token counting
  (node_worker.py:360 area — NVIDIA pins already provisional, but this
  blocks claim-bearing NVIDIA results); strict raw-lineage verifies
  powermetrics only (cli.py:713); zero-length window reduces to a
  "successful" 0 J strict-valid bundle (reduce.py:751).
- B8 RIGOR design blockers: legacy headline claims never passed the
  advertised gates (need explicit legacy-L1 waiver labeling, not silence);
  data-dependent repetition top-ups with ordinary 95% CIs (analysis_plans
  102/124/146) invalidate nominal coverage absent a sequential policy;
  split-pack Q1 compares split against the observed MIN of two monolithic
  baselines — post-hoc comparator selection bias.

## Severity adjudications (lead)

- Zero-MAD outlier masking (aggregate.py:431 returns "mad_zero_not_computable",
  flags nothing at [5,5,5,5,100]): SHOULD-FIX with the reason-code nuance.
- Token total: config-counts-win vs D-058 runtime-observed (reduce.py:278
  docstring): SHOULD-FIX, cheap, do before Window A.
- Gross request energy wrongly requiring idle-drift evidence (reduce.py:424
  require_drift always true): SHOULD-FIX pre-Window-A (false-blocks gross
  claims — the fail-closed gate would reject valid evidence).
- "Campaign-ready" language: SHOULD-FIX → "pre-campaign software review
  cleared; execution gated on shakedown, calibration, quiet machine, backup."
- Interpolation bound one-edge-only (2x understatement): SHOULD-FIX.
- PROJECT_STATUS accretion (4 stacked updates + process essay): SHOULD-FIX
  restructure per TOPDOCS design judgment.
- Hailo `if-viable` remnants, milestone auth-gate staleness, D-054 170-vs-180
  discrepancy: NITs, batch into one hygiene pass.

## Discussion items (design-bearing — for counterreview)

1. **Process restructure** (META): adopt the direction, staged — (a) now:
   RUN_STATE compaction to single next-action pointer, stop council
   pointer-body entries, retire planning_reflection_protocol as standalone
   intake (fold goal/fences/acceptance into queue rows); (b) next session:
   generated current_policy.md + per-session findings.jsonl; (c) defer the
   full machine-readable queue/state file. Rationale: big-bang migration
   mid-project risks exactly the state-drift it cures.
2. **Layer-drop rule**: replace "two zero-yield sessions" with "evaluate
   after ≥3 APPLICABLE sessions, count accepted unique defects separately
   from false-positive suppression and clean verifications, weight by
   severity/avoided loss." META's integration-review sequence (zero, zero,
   then five real seams) falsifies the current rule.
3. **Sequential-sampling remedy** (RIGOR B8): full alpha-spending machinery
   is oversized for a capstone. Proposed: freeze per-pack n at plan time;
   any post-hoc top-up demotes the result to exploratory (labeled), never
   pooled into the confirmatory CI. Question to examiner: does that pass a
   hostile defense?
4. **The stop line** (NEGSPACE): recommend to Ed as a decision entry: no new
   breadth (new packs, registry expansion, site features, meta-process
   growth) until (i) grading rubric + calendar captured, (ii) off-machine
   backup done, (iii) Window A floors + baselines collected, (iv) one
   end-to-end bundle→figure→report-page slice exists.
5. **Governance remedies** (REVERSE): dated breach addendum naming the four
   D-031 commits + retroactive independent review of their combined diff;
   manifest repair addendum pointing at recoverable observer-index evidence
   (no invented hashes); stop-card override addendum for the advisor-site
   episode (user direction existed but was never recorded as an override);
   credential-boundary push procedure.

## Immediate corrective actions (this session, bookkeeping-class)

Fix the three claim-surface blockers in living docs only (README token
claims + basis labels; PROJECT_STATUS D-053 rule bullet; RUN_STATE stale
block deletion); record C-027 council entry; file docs/reviews/ artifact;
add queue rows for every accepted finding (contrast engine gets an owner).
Historical reports remain untouched (addenda only).

## New-model calibration note (model-version scoping doctrine)

First gpt-5.6-sol xhigh production session: 7/7 lenses returned OK, zero
stalls, zero thin outputs (11.8-19.9 KB), wall-clock ~13-32 min each.
Behavior upgrades vs 5.5 baseline: unprompted premise correction (NEGSPACE
corrected four prompt premises; RIGOR caught one), every one of ~15
lead-verified file:line claims accurate, worked numeric counterexamples
supplied unprompted (STATS). Zero confirmed false positives so far.
Candidate doctrine change: proceed to the pre-registered sealed A/B for
delegation-boundary expansion; treat 5.6-sol-xhigh as the default review
model immediately.
