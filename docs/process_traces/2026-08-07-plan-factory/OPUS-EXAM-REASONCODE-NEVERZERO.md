# Opus examination — DRAFT-REASONCODE and DRAFT-NEVERZERO

Examiner: Opus 5, 2026-08-07. Ground truth: desk worktree at `3b5a794`+ (the
plan-factory directory advanced during this exam; REASONCODE's final message
landed mid-read and this exam reads the completed version, 13798 lines).

Everything asserted below as "verified" was checked against primary evidence in
this checkout, not against the drafts' own claims. Verification notes are
inline so the magistrate can audit the audit.

---

## PLAN 1 — DRAFT-REASONCODE (member_id→reason_code plumbing + spec reconciliation)

### Verdict: **ACCEPT-WITH-AMENDMENTS**

This is a strong plan. It is right on the four questions that matter most, and
it produced one finding I independently confirmed and that nobody else had:
the ratified spec's authority pointer is broken.

**What it gets right (verified, not taken on trust):**

1. **Append-compatibility is real, not asserted.** I checked every reader.
   `_validate_row_uncached` (`joulewise/whole_window.py:4113-4692`) checks
   `schema_version` equality against the same `.v1` constant both writers
   emit, then reads named fields with `.get()`; it never enumerates or rejects
   unknown top-level keys. `basis_present = "evaluation_basis" in row`
   (`:4121-4127`) means "old row lacking a field" is already a first-class
   supported case. `parse_campaign_log_bytes`
   (`joulewise/campaign_provenance.py:452-465`) is object-only JSONL with no
   per-record schema. `_require_exact_keys` (`joulewise/idle_admission.py:80-92`)
   *does* reject unknown keys but its call sites validate the campaign-policy
   `idle_admission_extension` sidecar, never a log row. **Old logs still
   parse. The claim holds.**
2. **The two existing emitters already emit different top-level key sets**
   (Site A `_run_whole_window_verdict_locked` `scripts/run_campaign.py:5312-5364`
   emits `waived_bundles`/`occurrence_supersessions`/`window_membership`/
   `salvage_dangler_exclusion`; the AXI path at `:6780-6819` does not), and
   every reader consumes both. Key-set variance is an exercised property, so
   the risk of an optional field is genuinely low.
3. **It refuses to assume ratification authority.** §2 builds an amendment
   packet, cites S4, requires a cold instance + cross-model contract refuter,
   and demands a lead ruling with a newly allocated decision ID. This is
   exactly the correct posture and it is not hedged.
4. **Backfill is custody-safe by construction** — append-only annotation
   records keyed by `target_line_sha256`/`target_row_sha256`, conflicting
   annotations produce a conflict rather than a winner, an annotation never
   changes the target's claim authority, and unrecoverable attribution is
   recorded as `unresolved` rather than reconstructed. It also correctly
   defers the whole backfill out of the pre-window diff. The chosen shape
   matches the repo's existing `campaign_occurrence_supersession` precedent
   (`joulewise/whole_window.py:75-77`, writer `scripts/run_campaign.py:5087-5103`,
   self-seal `supersession_entry_sha256`).
5. **The D-083 pointer defect is real.** `docs/phase_2/refusal_scope_spec.md:72`
   cites "Decision-log amendment: D-083". `docs/decision_log.md:108` and `:5131`
   show D-083 is the B3 effective-clearable-effect disclosure ruling — a
   different subject, same date. Worse than the draft says: `grep -n
   "refusal_scope\|refusal scope"` over `docs/decision_log.md` returns **zero
   hits**, so the refusal-scope spec has *no* decision-log row at all. The
   ONE-home spec is ratified by a document that the ledger does not record.

**Why not ACCEPT:** the plan leaves the single most custody-critical design
decision unpinned (A1 below), and it proposes a refactor of the claim-bearing
verdict function three days before the first measurement night without a
characterization test to prove behavioural identity. Both are correctable in
the plan text; neither is discretionary.

### Amendments

**A1 (blocker — pin field placement; the plan is currently ambiguous where it
must be exact).** §3 shows `"member_failures": [...]` without saying whether it
is a top-level row key or a member of `idle_admission_core`. This is not a
style question. `whole_window_refusal_reasons` computes a semantic-identity
digest over an explicit six-key projection — `status`, `bundle_ids`,
`campaign_policy`, **`idle_admission_core`**, `row_provenance`,
`evaluation_basis` (`joulewise/whole_window.py:4761-4772`) — and returns
`whole_window_verdict_conflict` when same-basis rows disagree. Put the field
inside `idle_admission_core` and a legacy row and a new row for the same basis
compare unequal, i.e. a re-verdict of any historical window refuses. Amend to:
*`member_failures` is a TOP-LEVEL sibling of `idle_admission_core`; the
six-key projection at `whole_window.py:4761-4772` is NOT modified; §4's
"preserve the existing semantic comparison" is satisfied by placement, never
by editing the projection.* Add a test asserting the projection's key list is
byte-unchanged.

**A2 (blocker — characterization test before the refactor).** §3 asks for
`idle_admission_core_verdict` (`scripts/run_campaign.py:4094-4382`) to be
refactored into a shared helper. That function *is* the claim-bearing verdict
computation, and its per-member codes are currently destroyed by
`conditions.update(...)` set-union at `:4148,4157,4162,4166,4177,4189` before
`section["conditions"] = sorted(conditions)` at `:4381`. Amend the test list
to add, as item 0: a golden characterization test over recorded fixture
inputs that pins the canonical sha256 of the whole `idle_admission_core` dict
and the row `status`, **generated at the pre-refactor commit and asserted
after**. A refactor that changes one sorted list silently is the exact defect
class that would strand a night.

**A3 (blocker — replay verification must not touch custody roots).**
`scripts/mint_floor_artifact.py:1128` pins `campaign_log_sha256` over the
entire `campaign_log.jsonl` bytes, re-verifies at `:1167-1181`, embeds it at
`:1477`, and re-checks issued artifacts at `:1739-1741`
(`campaign log sha256 mismatch`); the analysis engine binds the same digest
(`joulewise/analysis_engine/inputs.py:995-1001`). Therefore **any verification
re-run of `--whole-window-verdict` against a historical runs root appends a
row and invalidates that root's issued-artifact pin.** The plan does not say
this. Amend: all replay/verification runs execute against copies in a temp
tree; no runs root under `/Users/edr/code/JouleWise/runs_*` or
`/Users/edr/JouleWise-window-custody/` is ever a target; the unit's WRITE_SCOPE
non-scope list gains "any `campaign_log.jsonl` under any runs root".

**A4 (sequencing — do not put the urgent code behind a documentation gate).**
§7 gates the implementation lane on ratification of the spec amendment. The
plumbing is the URGENT item (evidence lost forever if the nights run without
it); the amendment is documentation of behaviour that S2 already defaults
correctly (`Unknown code → GLOBAL`). Amend to two independent lanes: the
plumbing lands under the readiness gate on its own merits, carrying **no scope
classification in the row** (see A5); the spec amendment runs its own cold-gate
track and may land after the nights. **This is a magistrate ruling, not a
lieutenant call** — present it as such, with the plan recommending decoupling.

**A5 (make "attribution ≠ scope" a mechanism, not a caution).** §8 lists it as
a risk. Amend §3/§4 normatively: the record carries exactly
`{member_id, reason_code, detail}` and **no scope field, ever**; and add a
test that the local/global routing path produces identical results with
`member_failures` present, absent, and populated with hostile values. Without
that, the first reader to see `member_id` next to a code will infer
metric-locality, which is precisely what S1 forbids and what the 2026-07-29
cold gate ruled on.

**A6 (sort key is coupled to free text).** §3 sorts by
`(member_id, reason_code, detail)` while also forbidding duplicate
`(member_id, reason_code)` pairs. The third key is therefore dead weight that
makes row bytes depend on prose — and if `detail` ever renders a float or a
timestamp, ordering becomes environment-dependent. Amend: sort by
`(member_id, reason_code)`; bound `detail` explicitly (ASCII, ≤ 256 chars, no
absolute paths) and declare it non-load-bearing.

**A7 (the amendment list must cover the DORMANT vocabulary, not the observed
20).** §2 item 2 asks for the full emittable inventory but §2 item 3 then
enumerates only the 20 observed spellings, and §8 leaves the choice open. The
codes that will bite during D-117 are precisely the ones that have never
fired. Code-derived inventory from this checkout, beyond the draft's 20:
`cpu_baseline_telemetry_malformed`, `cpu_baseline_sample_count_insufficient`,
`gpu_idle_admission_unknown`, `adapter_observations_missing`,
`adapter_description_changed`, `adapter_power_source_changed`,
`neg8_bracket_rel_delta_exceeded` (`joulewise/idle_admission.py:44-67`);
`neg8_drift_bound_underived`, `neg8_idle_sub_drift_bound_underived`,
`neg8_bracket_idle_sub_abs_delta_exceeded` (`joulewise/whole_window.py:93-103`,
noting `CONDITION_NEG8_GROSS_POINT_DRIFT_EXCEEDED` at `:97` is an *alias* of an
already-listed value — do not double-count it);
`idle_admission_extension_unconfigured` (`scripts/run_campaign.py:4126`);
`whole_window_campaign_membership_ambiguous` (`:4919-4926`);
`thermal_pressure_elevated_in_window` (`joulewise/environment_admission.py:370`,
folded in at `scripts/run_campaign.py:4148,4157`); plus the 15
`instrument_calibration_*` family folded at `~:4320`. Amend §2 item 3 to
ratify the full emitter census with every entry GLOBAL, and add a registry
test that FAILS when a new emittable spelling appears unregistered.

**A8 (bound the amendment to GLOBAL-only).** State explicitly in the packet:
this amendment may register codes only as GLOBAL, matching the S2 default, so
it documents existing behaviour and moves nothing. **Any proposal to register
any of these codes as metric-LOCAL is a distinct S4 scope move requiring its
own cold gate.** Without that sentence a future reader can treat the packet as
precedent for local registration by the same route.

**A9 (name the readiness-record dependency and a no-go cutoff).** D-113 cl.7-9,
surfaced as the `FROZEN-PLAN-READINESS-RECORD` start-dependency of
`MET-WINDOW-C-01` in `docs/process/state_kernel.json`, requires a "clean pinned
head". A verdict-path change landing *after* the readiness record is signed
invalidates it. Amend: the unit completes, is adjudicated, and is head-pinned
BEFORE the readiness record is signed; and predeclare the abort — *if the unit
is not green by <cutoff>, the nights proceed without it and member-failure
evidence stays free-text for those three windows.* The nights are the P1
critical path; a plumbing unit must never become their blocker.

**A10 (AXI-row validator tolerance).** §4 validates `member_id` membership in
`bundle_ids ∪ excluded_bundles ∪ waived_bundles`, but the AXI emitter
(`scripts/run_campaign.py:6780-6813`) emits no `waived_bundles` key at all.
Amend: absent partition keys are treated as empty sets, never as a validation
failure — and add that case to test item 2.

**A11 (repair the authority pointer as part of the packet).** Beyond the draft's
note: there is no decision-log entry for the refusal-scope spec at all. The
packet must (a) mint the new ID for this amendment and (b) either locate the
2026-07-29 cold-gate ruling's true ID or record that the spec was ratified
without a ledger row, and fix `refusal_scope_spec.md:72` accordingly.

### Three highest-risk gaps

1. **Unpinned field placement (A1).** One plausible implementer choice —
   nesting inside `idle_admission_core` — silently converts every same-basis
   re-verdict into `whole_window_verdict_conflict`. The plan's own "preserve
   the semantic comparison" line invites the *worse* fix (editing the
   identity projection) rather than the safe one (placement).
2. **An unguarded refactor of the verdict function days before the nights
   (A2).** The plan's stated goal is minimality, but §3 refactors the exact
   function that computes claim-bearing conditions, with no behavioural-identity
   test. Tests 1-13 all test the NEW field; none pins the OLD output.
3. **Schedule coupling (A4 + A9).** As written, urgent evidence plumbing is
   downstream of a cold-gate documentation ratification and upstream of nothing
   — no readiness-record dependency, no cutoff, no ship-without path. That is
   how a small good unit ends up delaying the P1 critical path or landing hot.

---

## PLAN 2 — DRAFT-NEVERZERO ("the price of never-zero" subsection)

### Verdict: **ACCEPT-WITH-AMENDMENTS**

The arithmetic specification is **correct** — I checked every formula against
primary sources rather than the draft's citations.

**Arithmetic verification:**

- D-102 pin 3 (`docs/decision_log.md:6317-6321`) reads verbatim
  `A_s = max(observed_drift_s, 0.010818)`; `B_operative = max(B_pre, B_post) + A_s`,
  "embedded ONCE in the authenticated operative fiducial bound … no second
  calibration-drift energy term anywhere downstream (D-078 cl.11 single-count)".
  The draft's §1 matches this exactly, including the single-count discipline.
- The rule is **implemented at HEAD**: `joulewise/calibration_bracketing.py:1235-1250`
  computes `allowance = max(drift_decimal, screen)`,
  `operative_bound = endpoint_max_decimal + allowance`, records
  `"rule": "max(observed_drift_s,bracket_screen_s)"`, `"embedding_count": 1`.
  So the `d102` scenario is the production path, not a reconstruction.
- Component formulas match `docs/phase_2/detection_floor.md:103,107` character
  for character (`floor_abs_j = max(max_i|r_i|, t·s_r·sqrt(1+1/n))`;
  `floor_cmp_j = max(max_i|δ_i|, |mean δ| + t·s_δ·sqrt(1+1/n))`), and the ABBA
  δ and its half-width `(w_A1+w_B1+w_B2+w_A2)/2` are the correct worst-case
  propagation for `δ = (B1+B2-A1-A2)/2`. Small-sample guard `5 ≤ n < 10`
  matches `:111-112`.
- **Operator order is right and I confirmed it numerically against the retired
  artifact**: `df-ph-decode-floor-mint1.json` gives
  `corner_widened_guarded_floor_j 2.9398659385551955 + allowance_j 0.652271753365838
  = 3.5921376919210335 = floor_abs_j`, and
  `6.795813690761627 + 0.5812720449734456 = 7.377085735735073 = floor_cmp_j = floor_gate_j`.
  So: corner-widen → guard → **add the family-matched energy allowance per
  component** → `max(abs, cmp)`, never sum. The draft's steps 6-7 are exactly
  this, and its insistence on armwise max at the claim (step 8) matches the
  lens-3 audit's "max-not-sum; armwise max at claims".
- The draft's decision to hold the NEG-8 **energy** allowance fixed across
  timing scenarios is correct and has a warrant it does not cite:
  `detection_floor.md` (CAL-REBRACKET-01) states "Anchor points and NEG-8 point
  screens remain identical" under widening.
- DIAGNOSTIC labelling is right and unusually careful: retired mint1 and the
  D-110 re-mint rows are labelled non-claim, the refused corrected-selector
  reports are explicitly barred from being described as issued floors, and
  §2 refuses to fill missing prefill cells "by transport or borrowing".
- Re-runnability is designed in: manifest-pinned inputs, `--mode diagnostic|d117`,
  separate output directories, determinism check (twice, byte-identical), and
  a sequencing rule that the D-117 directory lands only after alpha/beta/gamma
  pass. Prospective roots match the plan-freeze memo
  (`docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:219,465`),
  so they are not invented.

**Why not ACCEPT:** the paper-facing half has a specific, checkable honesty
defect (N1/N2), and three of the specification's inputs are asserted as
literals where the governed value is an artifact field (N3).

### Amendments

**N1 (blocker — the title and anchor collide with an existing, different
"never-zero" in the paper).** `docs/paper/draft-v1.md:96` already has a §4
subsection titled **"Measured, never-zero drift allowance"** — and it is about
the NEG-8 **energy** allowance (reference runs, gross vs idle-subtracted
families, excursions). The **timing** rule this subsection is about is
introduced in §3 at `:56` ("even a perfectly agreeing bracket carries the full
screening allowance"). The draft therefore (a) proposes a §8 subsection titled
"What the never-zero rule costs" that a reader will attach to the §4 *energy*
allowance, and (b) hangs its forward reference off §4 — **the wrong section**.
Amend: title the subsection to name the quantity ("What the never-zero
**timing** allowance costs"), place the forward reference at the end of the §3
bracket paragraph (`:56`), and if a §4 pointer is kept, make it a
disambiguation ("this is the separate energy allowance"). The portfolio
synthesis already flagged this exact confusion risk; the plan half-inherited
it (one distinguishing sentence) and then mis-anchored anyway.

**N2 (blocker — the counterfactual verdict is not a result about the system).**
The proposed table's last two columns are "Verdict without / with" and "Flip?".
The "without" verdict is a desk-computed counterfactual under a rule the
project does not use, backed by no minted artifact. "Do not promise a flip" is
not enough. Amend: (a) the counterfactual column is explicitly labelled as a
sensitivity computation, never as a floor or a verdict the project holds;
(b) only the `d102` column is artifact-backed and it must be stated as such;
(c) a one-sentence rule in the prose: *the flipped verdict is an arithmetic
property of the rule, not a claim about the two stacks.* Otherwise a reviewer
reads "verdict flips without the bound" as a published negative result.

**N3 (0.010818 must come from the issued acceptance artifact, not a literal).**
Production reads the screen from the registered acceptance artifact
(`calibration_bracketing.py:1235`, `max(drift, screen)`), and D-102 pin 2's
identity-epoch freshness triggers can force a re-derivation — the
night-hardening L4 finding is *exactly* that a hardcoded scalar is screened in
place of the issued artifact, and it names "de-duplicating the hardcoded
literal" as part of closure. Amend: the manifest carries the acceptance
artifact's hash and the screen is read from it; the script refuses if the
screen ≠ the ratified `0.010818` rather than silently computing a different
counterfactual; the paper prints the artifact-sourced value.

**N4 (feasibility of the `legacy_zero` / `observed_only` seam must be a step 0
probe, not a NEEDS_SCOPE hope).** §7 says "if the analysis cannot use the
existing in-memory re-reduction seam without changing `joulewise/**`, return
NEEDS_SCOPE" — correct instinct, wrong placement. Both counterfactuals require
driving the authenticated consumption session with an *externally supplied*
operative bound; if no such parameter exists, the only routes are monkeypatching
production or reimplementing floor arithmetic in the desk script. **A shadow
reimplementation of claim arithmetic whose numbers enter the paper is the worst
outcome available here.** Amend: make the seam probe the first deliverable,
before any manifest work, with an explicit rule that a private
reimplementation of the reducer or the corner enumeration is forbidden.

**N5 (mint1 parity: full precision, and a predeclared stop).** Verification
step 2 says "including the six-decimal `7.377086`". The artifact's value is
`7.377085735735073`; a six-decimal match would hide a 1e-7 divergence. Amend to
require exact reproduction of `floor_abs_j 3.5921376919210335` and
`floor_cmp_j 7.377085735735073`, and predeclare the failure branch: if parity
fails, **stop and report**, do not tune — mint1 also predates the D-109/D-110
selector repair, so a mismatch may be code-era, and the honest outcome is a
recorded residual, never a fitted one.

**N6 (derive the evidence label from the inputs, not from `--mode`).** The
outputs carry `DIAGNOSTIC_NON_CLAIM` or `D117_PROSPECTIVE`. As specified, an
operator flag decides which — one typo mislabels a diagnostic number as
prospective. Amend: the label is derived from the inputs' own issuance/claim-
licensing state (issued floor artifact + passed verdict + claim-bearing
policy), and the run refuses if `--mode` disagrees with what the inputs prove.

**N7 (the desk artifact must not be schema-compatible with a floor artifact).**
Verification step 6 runs `validate_floor_artifact(...) == []` on "the final
four-cell artifact", conflating the governed mint with the sensitivity output.
Amend: the sensitivity output gets its own schema id (e.g.
`joulewise.never_zero_sensitivity.v1`) and MUST fail floor-artifact validation
by construction, so no pipeline can ever consume it as a floor; step 6 applies
only to the governed D-117 mint.

**N8 (prefill has no diagnostic validation — say so and cover it with
fixtures).** The historical corpus is decode-only (mint1 has the single cell
`df-ph-decode-floor`), so the diagnostic stage validates the method on decode
only, while two of the four reported cells are prefill riders. Amend: state
this as a named limitation, add synthetic-fixture tests for the prefill path in
`tests/test_analyze_never_zero_cost.py`, and register the dependency on the
U3/U10 mint units delivering prefill-metric minting at all — without them the
four-cell artifact does not exist and the subsection cannot be written.

**N9 (generate the d117 manifest mechanically).** Hand-typed hashes are the L4
defect class. Amend: the `d117` manifest is generated from the frozen plan
record, pinsets, and issued artifacts by a script, and the run refuses on any
hand-edited field. Also treat the memo's root identifiers as *proposed* — D-117
cl.5 defers immutable identifiers to plan freeze — and resolve them from the
frozen record.

**N10 (specify the cost denominator and the guarded/unguarded tracks).**
"Cost, J (%)" needs its base declared (percent of the `observed_only` operative
floor, recommended). And the artifact should emit both
`corner_widened_{un,}guarded_floor_j` and the post-allowance values under each
scenario, so parity against the mint's own field names is checkable rather than
inferred.

**N11 (custody hygiene for the re-reduction).** Add explicitly: scenario
re-reductions run in memory or into a temp tree outside every custody root; no
scenario output is ever written under a runs root (an appended byte there
breaks the issued artifacts' whole-file `campaign_log_sha256` pin at
`scripts/mint_floor_artifact.py:1128,1739-1741`); the script records the code
head sha and refuses on a dirty worktree.

### Three highest-risk gaps

1. **The paper collision (N1).** Placing a *timing* sensitivity subsection
   behind the paper's existing *energy* "never-zero" subsection, under a title
   that repeats the phrase, produces a paper that appears to quantify one
   allowance while actually quantifying the other. This is the single
   highest-consequence defect in either plan, because it survives into print.
2. **The counterfactual verdict presented as a finding (N2).** The plan's
   honesty instincts are good but stop one step short: it forbids *promising* a
   flip while still tabulating a "verdict without" that no artifact backs.
3. **The re-reduction seam (N4).** If the seam does not accept an external
   bound, the plan's own guardrail (NEEDS_SCOPE) is the *good* outcome; the bad
   outcome is a desk-script reimplementation of the floor arithmetic producing
   paper numbers outside the governed path. Probing this first is cheap and
   decides whether the unit is viable at all.

---

## Cross-cutting note for the magistrate

Both plans correctly identify their own ratification boundaries (REASONCODE §2
S4 cold gate; NEVERZERO §8 six open rulings). Two decisions in this pair are
**not** lieutenant-decidable under rule 11 and should be routed deliberately:
(i) REASONCODE A4 — whether the pre-night plumbing may land ahead of the spec
amendment; (ii) NEVERZERO N2 — whether a counterfactual verdict may appear in
the paper at all. Both are stop/scope judgments, not implementation details.
