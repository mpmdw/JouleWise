# Cold Fable gate ruling on packet 40 (magistrate ruling 17) — 2026-09-04

Judge: cold Fable instance, single foreground session, no subagents. `$OUT` was
unset; this path was chosen by the judge. Auto-loaded: global `~/.claude/CLAUDE.md`,
project `CLAUDE.md`, memory index `MEMORY.md` (not relied on). Not read:
CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, narrative state, the enclosure
branch diff, anything outside the manifest (including the refuter's file 42).

## 0. Digest verification
- Charter expected `099de884b1d0…95d81`; observed `099de884b1d0…95d81`
  (method: `shasum -a 256` independently, plus validator receipt
  `digests.charter_sha256`). Match.
- Packet expected `73d2a52a9e96…b6419`; observed identical by `shasum -a 256`.
- Validator: `result: PASS`, 36/36 exhibit digests observed == expected,
  `judge_handoff_bound: false`, `binding_scope: validation_time_observation_only`.
  PASS is custody only, not merits or launch authority.
- HEAD fffd9333; `git diff e323f1aa HEAD` over joulewise/, docs/contracts/,
  docs/decision_log.md is empty, so e323f1aa cites hold at HEAD.
- Word-level diff of 17 §B against 16's addenda: only the `[M]` sentence
  (17:73-74) and the D-161 line (17:107-108) are added; the rest is verbatim.

## 1. Executed witnesses (this session, from repo root)
P1 (02:150-164 snippet):
```
interval_average_point_J=9.000 interpolation_bound_J=0.000 envelope_J=[8.800, 9.200]
two_gate_example outcome=direction_supported claim_ready=True
```
P2 (02:175-190 snippet):
```
synthetic_common_time_shift_ratio=2.250368 passes=True
issued_shared_energy_sign_ratio=1.500000 passes=False rule=d165_shared_sign_local_corner_replay.v1
```
P3 (02:201-214 snippet): `renderer_exit_code=0 … contains_fixture_label=False
contains_old_models=True published_language=True` (pre-cure counterexample stands).
14-V1: `fixed … R=3.000000 / rotated … R=1.073827 / null ABBA unchanged … True`.
max(F,h+B) probe (`evaluate_claim`, F=5, positive direction, decision =
metrology ± B): (6,h=.1,B=4)→direction_supported; (10,7,4)→not_resolvable;
(5,.1,4) |x|=F → not_resolvable; (5.0000001,.1,4)→direction_supported;
(9,4,4) max=8 → supported; asym ci=[0.5,6.2] → supported; ci=[-0.1,6.2] → unresolved;
x=-6 symmetric → supported. Both inequalities are strict (`claims.py` excerpt L7,
L34-36).
Strict-comparison probe (Q-17-1 crux): stored
`tests/fixtures/d117_v2_production/strict_seed_bundle/summary_metrics.json`
(`reducer_version 0.5.2`) dispatched via `_strict_reducer_version_dispatch`
gives `absent_tolerance=['idle_baseline.gpu_freq_mhz_mean'] tolerate_fresh_nulls=False`
(`cli.py:845-846`); a fresh dict with the two enclosure keys added yields
`differences=['phase_partial_record_enclosure_j','phase_partial_record_enclosure_reason_code']`.

## 2. Rulings

### Q-17-1 — AMEND (REJECT as written). Severity MATERIAL.
- A AFFIRM. Deciding: P1 tail (point 9.000, envelope [8.8,9.2] vs same-record
  totals [8,10]); `run-bundle-layout` excerpt is the contract's overlap estimand
  (11:19-21 quotes :805). 17:65-69 states it correctly and completely.
- B AFFIRM. Clause-11 excerpt L45-47 ("exactly the largest false effect") and
  L22-24 ("STRUCTURALLY PERMANENT") are the withdrawn assertions; L47-51
  (labelled path), L56-63 (two roles), L63-65 (no double-count deletion) are
  preserved by 17:69-72. F+B non-gating: verified by the probe (6 J admitted at
  F+B=9).
- C AMEND. The five conditions are not proved by any manifest exhibit (packet
  §13.1), and condition (iii)+(iv) as the seat built them are unsatisfiable at
  this head: exhibit 30:163-164 puts the field on the EXISTING current versions
  0.5.2/0.6.2, yet `_strict_summary_differences` (cli.py:654-700) with the
  current-version tolerance (cli.py:845-846) rejects every stored 0.5.2/0.6.2
  summary lacking the key — probe above; the tracked strict seed bundle is one
  such summary, and cli.py:478 applies the same comparison with no tolerance on
  the 0.6.x arm. Either those summaries are re-reduced and re-pinned (custody
  churn per 11:30-35) or the key enters a tolerance set, the ignore-key
  exception (iii) forbids. Exhibit 30 lists no test_cli_run and no
  strict-validation run (30:29-148), so 17:16's "tests.test_cli_run … 298 OK" is
  unsupported by the manifest. Deciding exhibits: cli.py:845-846 and :654-700
  (probe), 30:163-170, 16 §B ("No exhibit supplied; desk default stands").
- Replacement for 17:17-21: "Ruling: for this submission the enclosure is the
  pinned desk script of 14:43-47 and 15:16-21 (appendix figure, one DERIVE row,
  authenticated inputs, each record once, negative/unsupported domains refused).
  A reducer field may replace it only after a later gate reviews a delta
  re-audit proving (i) an oracle for a window wholly inside one record; (ii)
  fixed-window scope declared in the contract and never added to frozen bounds;
  (iii) no new absent-tolerance or ignore-key entry in cli.py or the contract;
  (iv) the field introduced under NEW reducer versions named in the
  run_bundle_layout.md roster, with every stored 0.5.2/0.6.2 summary and pin
  proven to pass strict validation unchanged; (v) the branch diff, goldens and
  campaign identity/pin transition reviewed. Exhibit 30 does not satisfy (iv)."
- Addendum D-078 (17:65-74): ratifiable verbatim into docs/decision_log.md
  after deleting the editorial marker "[M]" (NIT). The enclosure sentence is
  placement-neutral and correct.
- Disagreement with 17: 17:13-17 ("the exhibit astra asked for now exists",
  "accepted CONDITIONALLY") and 17:16 test claim.

### Q-17-2 — AFFIRM. Severity NIT (v2 string change on new objects only).
- A: P2 re-executed: same synthetic common time shift gives 2.250 (passes) under
  a physical shift and 1.500 (fails) under the issued shared-sign replay
  (`dominance-closeout-L680-L700` L8-21 applies one sign to widths, no time
  coordinate; L40-70 L12-16 states the cancellation rationale being
  superseded). A uniform energy offset cancels from deviations-from-mean; a
  time shift enters as slope_i·Δt, member-specific, so it need not. Correct.
  "No proven conservatism" is the honest wording (12:40-50 reports a reverse case).
- B: relabel semantics preserve v1 bytes and every threshold/census/branch
  clause of the D-165 index row (R ≥ 2, R_cm < 2 withdrawal, not_applicable
  absolute). The "eight/four ratio" counts are asserted, not exhibited;
  §13.2 conditions this to semantics only — no completion is claimed.
- Addendum D-165 (17:83-91): ratifiable verbatim. Agree with 17:23-24.

### Q-17-3 — AFFIRM. Severity MATERIAL for the held migration (no claim of completion).
- A: D-083 body L52-55 ("effective bar = floor + claim-side … stays, as the
  correct description") is refuted by the probe: 6 J is admitted at F=5, B=4.
  Supersession of the description while preserving L39-41's rejection of an
  additive gate is exact.
- B: for metrology x±h and decision x±(h+B), the code's conjuncts are |x|>F
  (excerpt L7, strict), metrology excludes 0 (|x|>h), decision excludes 0
  (|x|>h+B, strict at the endpoint, L34-36). With B ≥ 0 the third implies the
  second, so the conjunction is exactly |x| > max(F, h+B). Verified at the
  boundaries (x=F fails; x=8=h+B fails as not_resolvable; x just above passes). Asymmetric case
  correctly deferred to actual endpoints (probe rows). Mathematically exact.
- C: v1 object is exact-equality checked at `detection-floor-L3340-L3360` L6-8
  and pinned in adapter_contracts.md:623-633; a v2 with gating:false cannot pass
  that consumer, so version-aware consumers are necessary — the proposal says
  so. Migration artifacts absent (§13.2); the addendum makes no completion claim.
- Addendum D-083 (17:75-82): ratifiable verbatim. Agree with 17:26-30.

### Q-17-4 — AMEND (REJECT as written). Severity MATERIAL.
- A AFFIRM: better-defensible. Floor packs pin prompt 0 (12:88-90 verified
  cites; 11:118-121 concedes the family carries no prompt identity); the
  absolute floor centres on one mean, so rotating the repeat arm converts R_abs
  into a prompt-variance test (14-V1 re-executed: 3.000 → 1.074 with noise and
  widths held). Prompt-0 contrast changes one generator and keeps the floor's
  question; Opus's mirror (11:126-137) re-pins both frozen packs and changes
  what the floor measures.
- B AFFIRM: V1 supports the same-condition question; the null ABBA identity
  shows additive prompt means cancel in comparative deltas, so no bias
  direction is established; 16 F2's correction is rightly kept (17:34-35).
- C AMEND: completeness cannot be affirmed — no dependency census exists
  (§13.3), and 14:86-88 named "manifests/projections" while 17:95 names
  "projections" only. Replacement sentence for 17:95-96: "Regenerate every
  artifact whose identity, digest or custody pin derives from the decode prompt
  selection — at minimum contrast configs, suite manifests, identities,
  projections and custody pins — as enumerated by a dependency census recorded
  in the supersession record before collection, and rerun the required clone
  proof."
- Addendum D-166: ratifiable only with that sentence substituted. Otherwise
  agree with 17:32-36.

### Q-17-5 — AMEND (REJECT as written). Severity MATERIAL.
- A: bounded in time ("until submission") and per task (stop time). Reversible
  only by the generic later-decision path: the text names no lifting authority
  and "submission" has no date (§13.4). The "Park" list (17:101-103) uses
  stream shorthand (AUTH, LINEAGE, MODULARITY, skill-distill) that a
  decision-log reader cannot resolve without narrative state — NIT, map to
  queue IDs at ratification.
- B AFFIRM: coherent; "missing evidence selects fallback" matches Q-17-6.
- C AFFIRM as internal cuts: 6 September is Sunday, two days out; 8/9 September
  and the 48 h reserve are self-consistent; "authoritative earlier deadlines
  advance these cuts" handles the absent due date. The fanout-30 exhibit was not
  needed for this and proves no schedule.
- Replacement: append to 17:99-100 after "optional slots create no dependency":
  "'Selected' means a figure, table or refusal sentence listed in
  docs/paper/results-fill-registry.md at ratification. This rule expires at
  submission or on Ed's written instruction, whichever is first, and is amended
  only by a dated addendum; it never bars a fix to a claim-bearing path."
- Addendum ratifiable with that insertion. Agree with 17:46-47 on the 6
  September readiness cut over 15:41-42.

### Q-17-6 — AFFIRM. Severity MATERIAL (absent CLI exhibit; design-only affirmation).
- A: sentence exact (15:37, 16 Q6, 17:41-42).
- B: OR-01 row (results-fill-registry.md:921, read this session) already
  defines the before-comparison stage as "the authenticated window-admission
  outcome for the affected model" and refuses absent/unauthenticated/conflicting
  inputs, so binding through the seam's whole_window_verdict ref is the
  registry's own shape; DS-32/PG-08 rows (:885, :894) exist as amendable rows.
- C: the six-case acceptance is a requirement, not a completion claim; no
  transcript exists (§13.5) and 17 does not claim one.
- D: D-161 body L6-7 makes the operative test MISTAKE vs DELIBERATE; the five
  negative cases are mistake checks, and a stop/non-issuance receipt family
  defends only against a deliberate operator (11:158-160 vs 10:45-47,
  12:121-126). D-173 is PROVISIONAL (body L28-31); if vetoed or unlanded, the
  ruled fallback (17:46-47, 15:41-42) selects, so no authority conflict is
  unresolved. Sufficient without a receipt family. Agree with 17:41-47.

### Q-17-7 — AMEND (REJECT as written). Severity MATERIAL.
- A AFFIRM: closing a route that could regenerate D-078-voided joules is an
  evidence fence, the fail-closed class D-161 keeps (body L6-7).
- B AFFIRM: the census criteria (every artifact enumerated; omitted or
  status-voided under a first-class lint dialect; no joule, table, "primary",
  "manual review"; v1 trees byte-identical; regression + supported-flip kill)
  are the right proof shape (12:139-149, 11:172-187).
- C AMEND: 17:107-108 asserts a present state ("every producer under it emits
  void placeholders") that no manifest exhibit proves (§13.6) and that P3,
  re-executed at this head, still contradicts for the results renderer
  (old models, "operative floor is published", no fixture label). 17:49
  "RULED and executed" is unproven here. Replacement line: "D-161 addendum: the
  rpt001 capstone profile is a closed publication route for legacy energy
  values; every producer under it must emit void placeholders carrying no joule
  observation, result table, 'primary' or 'manual review' text; a census
  regression over every artifact the profile writes enforces this, and
  regeneration cannot reopen it."
- Ratifiable only as that rule text, with the census output attached at
  ratification.

## 3. Packet hygiene
- Unsupported paraphrase: 17:16 (test_cli_run, "298 OK") and 17:13-14 ("the
  exhibit astra asked for now exists") — exhibit 30 contains neither a strict
  validation run nor the 16 §B proofs (era-aware strict comparison, pin/identity
  transition). Affects Q-17-1.
- Completion asserted without exhibit: 17:49-51 "executed", 17:107-108 state
  claim. Affects Q-17-7.
- Editorial marker "[M]" in ratifiable text (17:73): Q-17-1 NIT.
- Compoundness: Q-17-1 bundles estimand, clause-11 withdrawal and placement as
  one unit; A/B are affirmed and their text is ratifiable independently of C.
- §13 absent-evidence inventory is accurate and complete for what the questions
  turn on; no absence forced a REFUSE because each affected proposition is a rule
  or acceptance test rather than a completion claim. Alternatives (10, 11, 12)
  are presented in full and symmetrically. No unresolved authority conflict;
  D-173's provisional status is disclosed in the excerpt.

No file other than this record was modified; no hardware, host or launcher touched.
