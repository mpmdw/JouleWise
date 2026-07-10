# Spec: SPLIT-AP (split pre-registration freeze) + AP-EDIT (AP/contract text corrections)

Status: ADJUDICATED 2026-07-09 (C-028) — rulings in `ADJUDICATION.md` in this directory AMEND this spec wherever they conflict with its body text

Queue rows: TASK_QUEUE.md 0o (SPLIT-AP) and 0p (AP-EDIT).
Sources: whole-project review §3 B8(b)/(c) and §7 rows RIG-4/5/10/11/12,
STA-12, ARC-10, ARC-12, NEG-7; lens-rigor findings 4, 5, 10, 11, 12;
lens-negspace finding 7; D-062 (fixed-n/demotion), D-053 (ratification),
D-002 (raw verbatim), D-048/D-049 (unchanged, referenced).

Fences: text amendments only — no code, no schema changes, no new lint
rules implemented (lint implications are noted per unit for the existing
`scripts/claims_lint.py` and future pack/claims-index linting). No dated,
already-executed pack is touched (none of the affected packs has executed).
Line numbers below are as of branch `c027-council-review` HEAD; match on
exact text, not line number.

---

## Part I — SPLIT-AP (docs/campaign_packs/split_suite_q1_q2_q3.md)

### SPLIT-1: Primary-estimand freeze (NEG-7)

DECISION: the split headline's single primary estimand is **composite
GROSS request energy under the two-already-powered-nodes service-state
assumption**. Composite idle-subtracted energy becomes named sensitivity
`SENS-SPLIT-Q1-IDLESUB`; provisioning-charged energy becomes named
sensitivity `SENS-SPLIT-Q1-PROVISION` (descriptive, L1 ceiling).

Justification (three legs):

1. Availability/symmetry: gross stage windows exist on every pairing;
   idle-subtracted composite requires idle baselines on both ends
   ("where both ends have idle baselines" in the current pack), so it
   cannot be the headline basis without conditioning the headline on a
   data-availability accident.
2. Conservatism against the favored hypothesis: gross stage-sum charges
   each node's full power (baseline included) during its stage windows,
   including serialize/transfer/deserialize overhead windows that
   monolithic runs do not have. Idle subtraction is the basis under
   which split most easily "wins" (NEG-7's exact vulnerability), so it
   must be the sensitivity, not the headline.
3. Consistency: the monolithic references and the existing floor rows
   (`DF-RQ-GROSS-*`) treat `gross_energy_j` as the primary request
   metric; the crossover contrast is then like-vs-like.

Service-state assumption, frozen wording: both nodes are treated as
already powered and warm (model loaded on the decode node before the
measured window, per the split_plan `decode_node_warm_state`); the split
question is the marginal energy of executing the request split versus
monolithic on either single node in that same two-node-powered state.
`SENS-SPLIT-Q1-PROVISION` charges the second node's measured idle power
for the full request duration (and, where reported, an amortization
note); it can only weaken, never create, a split win.

Exact replacement — Q1 row "Metric + exact window class":

OLD:
> Primary: `split_total_energy_j = prefill + serialize + transfer + deserialize + decode` reported as composite gross request energy and, where both ends have idle baselines, composite idle-subtracted request energy. Stage descriptors use gross phase windows: ...

NEW:
> Primary (single frozen estimand): `split_total_energy_j = prefill + serialize + transfer + deserialize + decode` as composite GROSS request energy, under the frozen service-state assumption of two already-powered warm nodes (decode-node model loaded before the measured window); the headline crossover verdict uses this basis only. Named sensitivity analyses, never headline-eligible: `SENS-SPLIT-Q1-IDLESUB` (composite idle-subtracted request energy, computed only where both ends have idle baselines, each end's own idle floor subtracted over its own stage windows) and `SENS-SPLIT-Q1-PROVISION` (gross composite plus the decode-oriented second node's measured idle power charged for the full request duration; descriptive, L1 ceiling). Stage descriptors use gross phase windows: ...
(rest of the field unchanged.)

Also amend Q3 "Metric + exact window class" energy-axis sentence: gross
composite is the primary energy axis; idle-subtracted appears only as a
`SENS-SPLIT-Q1-IDLESUB` companion figure, so the Pareto frontier cannot
silently switch basis.

Lint implication: pack-lint (future) should reject any split pack whose
Metric field contains two "primary" bases; claims_lint should map
headline split claims to the gross estimand id only.

### SPLIT-2: Dual predeclared monolithic references (RIG-5, B8c)

DECISION: kill the `min()` comparator. Both monolithic references are
predeclared, each gets its own contrast, and "split wins" is an
intersection–union verdict: split must beat BOTH references, each under
its Holm-adjusted interval within FAM-SPLIT-Q1-ENERGY-CROSSOVER.

Exact replacement — Q1 row "Estimator/formula":

OLD:
> For each frozen cell, estimate `delta_j = split_total_energy_j - min(monolithic_prefill_node_j, monolithic_decode_node_j)` with paired/block contrast when monolithic reruns are in the same campaign block; otherwise use predeclared unpaired contrast with session covariate.

NEW:
> For each frozen cell, estimate two predeclared contrasts: `delta_prefill_ref_j = split_total_energy_j - monolithic_total_j(prefill_node)` and `delta_decode_ref_j = split_total_energy_j - monolithic_total_j(decode_node)`, each with paired/block contrast when the monolithic reruns are in the same campaign block, otherwise the predeclared unpaired contrast with session covariate. Both contrasts enter the enumerated FAM-SPLIT-Q1-ENERGY-CROSSOVER contrast_id set and are Holm-adjusted within the family. "Split wins" in a cell is an intersection–union verdict: it holds only if BOTH Holm-adjusted 95% contrast intervals lie entirely below zero AND both contrasts clear the active floor gate; if either contrast fails, the cell verdict is "no crossover" or `not resolvable` per the three-way wording rule (D-053). No comparator may be selected after observing the data; the observed-minimum reference is forbidden.
(D-048 prediction-error sentence and the crossover sentence follow,
with the crossover sentence replaced:)

OLD:
> Crossover exists only where the split-total contrast is below zero and clears the floor gate.

NEW:
> Crossover exists only where the intersection–union verdict above holds (both references beaten under joint Holm-adjusted intervals, both clearing the floor gate).

Multiplicity note (same row set, "multiplicity_rule"): append
"; the Holm denominator counts both reference contrasts per cell in the
enumerated contrast_id set."

Lint implication: claims_lint flags any "split wins/saves/crossover"
wording not linked to both contrast_ids of the cell.

### SPLIT-3: Missing floor cells become execution gates (RIG-5 tail)

The pack already caps claims for composite `split_total_energy_j`,
`serialize`, `transfer`, and `deserialize` (no P2-015 rows). Upgrade
from claim-cap to execution gate.

Insertion — "Hardware Prerequisites" list, after the P2-015 bullet:

NEW bullet:
> - EXECUTION GATE (SPLIT-AP): headline Q1/Q2 split cells may not execute until P2-015 (or a successor floor pack) provides floor rows — or the frozen registry names an accepted AP-specific bound or combination rule — for composite `split_total_energy_j` and for the `serialize`, `transfer`, and `deserialize` windows on the frozen backend/boundary. Executing split bundles without these rows produces exploratory-only data; the AP rows may not be frozen while this gate is open.

Also append one sentence to each Q1/Q2 "Floor gate" field:
> Per SPLIT-AP, the missing composite/serialize/transfer/deserialize rows are an execution prerequisite, not merely a claim cap.

Lint implication: pack-lint should treat a frozen split AP row with
`pending-P2-015` composite rows as a freeze blocker.

---

## Part II — AP-EDIT (contract/plan text corrections)

### AP-1: "extrapolation" → held-out in-grid prediction (RIG-10)

File: `docs/contracts/analysis_plans.md`, AP-1 row "Holdout cells".

OLD:
> `(512,256)` interpolation and `(4096,512)` extrapolation holdouts; prediction errors must clear the AP-1 floor gate.

NEW:
> `(512,256)` and `(4096,512)` held-out in-grid corner predictions (interaction/additivity validation — both factor levels occur in the training grid, so neither is statistical extrapolation); prediction errors must clear the AP-1 floor gate. No extrapolation claim is available from this grid.

Lint implication: claims_lint adds "extrapolat" to the forbidden-wording
list for AP-1-derived claims.

### AP-2: Replication three-outcome rule (RIG-11)

File: `docs/campaign_packs/c5_3_1_3_5_replication.md`, C5-3.1 row
"Estimator/formula", second sentence.

OLD:
> Source-claim replication succeeds only when the original direction/verdict survives on the second unit or the difference is declared `not resolvable` under the frozen rule.

NEW:
> Source-claim replication has exactly three outcomes: `replicated` (the original direction/verdict survives on the second unit under the frozen contrast rule), `contradicted` (the second-unit contrast is resolvable and reverses the original verdict), and `inconclusive` (the second-unit contrast is below floor or otherwise `not resolvable`). `inconclusive` is never reported as successful replication. A `practically equivalent` verdict is available only via a predeclared equivalence margin and equivalence test frozen in the registry before execution.

Lint implication: claims_lint maps replication wording to the
three-outcome vocabulary; "replicated" claims require a resolvable
contrast.

### AP-3: D-062 demotion language at the three top-up sites (RIG-4, B8b)

File: `docs/contracts/analysis_plans.md`, rows "MDE/n sizing +
predeclared top-up rule" for AP-1, AP-2, AP-3 (the B8b-cited sites;
current text located at lines 110/132/154 — the review's 102/124/146
drifted).

Shared new clause (verbatim, appended per site after the site-specific
sizing text):
> Per D-062: confirmatory n is FROZEN at registry freeze from Window-A variance/MDE evidence (nearer 10 than 5 for near-floor contrasts); technically invalid runs are replaced under the predeclared replacement rule and are not top-ups; any outcome-dependent top-up permanently DEMOTES the contrast to exploratory — the original fixed-n analysis is reported regardless of direction, pooled estimates never carry nominal confirmatory coverage, and no later re-promotion occurs.

Site-specific replacements:

AP-1 — OLD:
> n=5 provisional; top up to n=10 for near-floor cells or contrasts before L3 wording (C-014).

NEW:
> n frozen at registry freeze (D-062): n=10 for near-floor cells/contrasts, n=5 elsewhere, sized from Window-A variance/MDE. [shared D-062 clause]

AP-2 — OLD:
> n=5 from D-014; no top-up required for L2 descriptive contrasts unless the observed contrast is near-floor.

NEW:
> n frozen at registry freeze (D-062): n=5 from D-014, raised to n=10 at freeze time only if Window-A evidence marks the contrast near-floor. [shared D-062 clause]

AP-3 — OLD:
> n follows the source campaign; near-MDE gaps may top up before ranking language, otherwise report `unresolved tie`.

NEW:
> n follows the source campaign and is frozen at registry freeze (D-062); gaps that remain near-MDE at the frozen n are reported `unresolved tie`, not topped up. [shared D-062 clause]

Companion sites (same file, same fix class — see DEVIATIONS): the
top-up/resize language in the AP-4/AP-5/AP-6 rows (current lines
176/198/220) and the header field description (line 30) should carry a
one-line pointer: "Top-up rules are governed by D-062 (frozen n;
demotion on outcome-dependent growth)." The split pack's Q1/Q2/Q3
top-up rows (split_suite_q1_q2_q3.md) get the same pointer as part of
the SPLIT-AP freeze.

Lint implication: claims_lint/pack-lint flag the strings "top up"/
"top-up" in confirmatory AP rows lacking a D-062 pointer.

### AP-4: Clear stale "pending ratification" markers (RIG-12, STA-12)

File: `docs/contracts/measurement_methodology.md`. D-053's status line
is explicit: "accepted (ratifies the 'pending ratification (C-023 S3)'
contract markers)". Three sites:

1. OLD: `Phase 4 Stage 4.0), amended 2026-07-09 pending ratification (C-023 S3):`
   NEW: `Phase 4 Stage 4.0), amended 2026-07-09 (C-023 S3; amendments ratified by D-053):`
2. OLD: `2026-07-09 (pending ratification, C-023 S3): at n <= 10, reports also run`
   NEW: `2026-07-09 (C-023 S3, ratified by D-053): at n <= 10, reports also run`
3. OLD: `- Amendment 2026-07-09 (pending ratification, C-023 S3): differences are`
   NEW: `- Amendment 2026-07-09 (C-023 S3, ratified by D-053): differences are`

Note: the leading "draft to be ratified against observed variance at
Phase 4 Stage 4.0" clause about D-014's original repetition/outlier
content is NOT cleared — D-053 amends the protocol wording but leaves
D-014's repetition counts standing; only the C-023 S3 markers are stale.

Lint implication: consistency-sweep/doc-lint rule — no live contract may
say "pending ratification" for a marker a decision-log entry has
accepted.

### AP-5: Adapter-contract split modes marked Phase-3-future (ARC-10)

File: `docs/contracts/adapter_contracts.md`, Runtime Adapter required
behaviors.

OLD:
> - Run prefill-only workload when supported.
> - Run decode-only or replay workload when supported.

NEW:
> - Run prefill-only workload when supported (Phase-3-future: no shipped RuntimeAdapter implements or is required to implement this yet; binding form lands with Phase 3 Stage 3.1/3.2 schema v0.2).
> - Run decode-only or replay workload when supported (Phase-3-future: same gating as prefill-only; the contract does not promise split modes the current adapters cannot express).

Lint implication: none for claims_lint; the contract stops promising
unimplemented capability, which is ARC-10's whole point.

### AP-6: Event-schema node-field + clock-domain reconciliation (ARC-12)

File: `docs/contracts/run_bundle_layout.md`.

(a) Composite layout listing (line ~357) contradicts the five-key
schema (~line 140-152, "not as a sixth top-level event key").

OLD:
> events.jsonl                 (controller + merged node events, node field)

NEW:
> events.jsonl                 (controller + merged node events; node role/identity in each event's `metadata`, five-key schema unchanged)

(b) Add one clock-domain sentence immediately after the composite
layout block (aligning with `node_worker_protocol.md` ~236 and D-002):

NEW paragraph:
> Merged node events in the composite `events.jsonl` are derived artifacts in the controller clock domain (node timestamps converted by subtracting the recorded `offset_estimate_s`); the raw node-domain event and telemetry files remain verbatim under `nodes/<role>/` per D-002, so the conversion is always re-derivable. Cross-node intervals shorter than the recorded offset bound are flagged, not attributed.

Lint implication: future composite-bundle validation asserts exactly the
five top-level event keys in merged events; any `node` top-level key is
a validation error.

---

## DEVIATIONS / OPEN QUESTIONS (for lead adjudication)

1. SPLIT-1 picks GROSS over idle-subtracted as primary. The defensible
   alternative (idle-subtracted, on "marginal work" grounds) was
   rejected for the availability and conservatism reasons above; if the
   lead reverses, `SENS` labels swap and the provisioning sensitivity
   still stands. Record the choice either way in the pack, not only
   here.
2. SPLIT-2 uses intersection–union (both Holm-adjusted intervals below
   zero). A stricter max-contrast joint interval is possible but adds
   machinery with no defense benefit; IU controls level for the "wins"
   claim by construction.
3. AP-3 scope: B8b names three sites; the same top-up idiom appears in
   AP-4/AP-5/AP-6 rows (lines 176/198/220) and in the field-definition
   header (line 30). This spec adds pointers there rather than full
   clause duplication — confirm or expand.
4. Review line references (analysis_plans 102/124/146; split pack file
   name `split_suite_campaign_pack.md`) have drifted vs the current
   tree (110/132/154; `split_suite_q1_q2_q3.md`). All OLD strings above
   were verified against the current files; apply by string match.
5. `SENS-SPLIT-Q1-PROVISION` charges the decode-oriented second node's
   idle power for the request duration; whether to also show an
   amortized-provisioning variant is left to figure-time judgment
   (descriptive only, so no registry impact).
6. Whether pack-lint (SPLIT-3, AP-3 implications) is implemented now or
   queued is out of scope for these text amendments; the rules are
   stated so the future linter row can cite this spec.
