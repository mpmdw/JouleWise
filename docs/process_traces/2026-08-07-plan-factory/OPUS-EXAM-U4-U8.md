# Opus examination — DRAFT-U4 and DRAFT-U8 (D-117 plan factory)

Examiner: Opus 5 (lieutenant lens: contract + execution).
Date: 2026-08-07.
Ground truth read: `desk` @ `3b5a794` (main); D-117 (`docs/decision_log.md` tail);
`docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`;
`docs/process_traces/2026-08-07-night-hardening/FINDINGS-REGISTER.md`;
`docs/phase_2/window_runbook.md`; `docs/phase_2/refusal_scope_spec.md`;
branch `impl/d117-u1-ledger-session` @ `f665dd4` (source read, not just diffstat).

## Custody note (read this first — it affects what was examined)

The two files named in the charge are **truncated snapshots**. Both
`docs/process_traces/2026-08-07-plan-factory/DRAFT-U4.md` (8,764 lines) and
`DRAFT-U8.md` (10,692 lines) were custodied at commit `3b5a794` *while the Sol
runs were still streaming*: DRAFT-U4.md ends mid-`exec` inside a source dump,
and contains **no final message at all**. The complete transcripts are the live
files `scratchpad/plans/draft-u4.md` (9,275 lines) and `draft-u8.md` (11,191
lines). I examined the final markdown blocks of the **live** files, extracted to
`scratchpad/plans/PLAN-U4-extracted.md` (lines 8765–9020 of draft-u4.md) and
`PLAN-U8-extracted.md` (lines 10693–10942 of draft-u8.md).

> **Amendment C-0 (custody, applies to the whole plan-factory batch):** re-custody
> all eight drafts from the live scratchpad files. The committed U4 draft does not
> contain the plan it is named for; anyone reviewing from the repo copy alone is
> reviewing nothing. Verify the other six drafts for the same truncation before the
> Fable review.

**Speculative branches produced no evidence.** `impl/d117-u4-regression` is at
`f665dd4` (== U1 tip, zero own commits) and `impl/d117-u8-readiness` is at
`0d9392f` (== main-ish, zero own commits); neither exists at origin. There is no
implementation diff to read as evidence of what the plans produce in practice.
This examination is of the plans on their own terms.

---

# PLAN U4 — synthetic three-window live-ledger regression

## Verdict: **ACCEPT-WITH-AMENDMENTS**

The plan is unusually strong on enumeration. I checked its coverage against the
memo's normative list line by line: all 7 memo proof obligations are named tests
(plus one extra on the issuance prefix), and all 12 memo refusal-vector bullets
decompose into 30 named tests with setups and oracles — 3/3 import, 4/4
session-receipt, 4/4 head/chain, 5/5 observation-universe, 4/4 binding, 5/5
endpoint-eligibility, systematic, range-expansion, count-boundary, and 2 of the
successor-prefix vectors staged. The arithmetic is self-consistent (8 + 30 = 38
active, + 5 staged = 43). Every API it names (`append_bracket_session_receipt`,
`finalize_bracket_session_slot`, `terminal_head_pin_for_session`,
`abort_bracket_session`, `build_calibration_bracket_binding`,
`discover_calibration_candidates`, `prepare_historical_import`,
`bootstrap_historical_import`, `_valid_acceptance_bound`, `MAX_AGE_S`) exists on
`f665dd4`, and every refusal code it asserts (16 checked) is a real spelling in
the landed taxonomy. That is a materially better grounding rate than the memo
itself achieved.

It is not ACCEPT because three of its central oracles are either **stale against
landed U1**, **unable to discriminate the implementation they name**, or
**structurally divergent from the operational path the three nights will run**.

### (a) Completeness — gaps

- **G1. The terminal-sequence oracle is stale.** The plan freezes "three receipts
  per window → sequence 85" from the memo, and *deliberately avoids the
  production writer* to hit it ("do not emit optional writer-claim receipts").
  But U1 as landed is not a three-receipt model: `calibration_ledger.py` defines
  `BRACKET_SESSION_SLOT_CLAIM_EVENT = "bracket-session-slot-claim"` and
  `claim_bracket_session_slot()` appends "one process-death-stable exclusive
  claim"; the operator-facing writer `scripts/validate_powermetrics_fiducial.py`
  calls `claim_bracket_session_slot` (line 409) before
  `finalize_bracket_session_slot` (line 467). The real three-night ledger is
  therefore 5 receipts/window and terminates at **91**, not 85. The plan
  acknowledges this in a risk bullet and then chooses the number over the path.
- **G2. Committed-pin cadence is unspecified for the happy path.** Step 5 says
  "advance the synthetic committed pin before opening the next session" with no
  statement of whether committed-pin enforcement is active during construction.
  Committed-pin discipline appears only inside one negative test
  (`test_uncommitted_terminal_head_pin_refuses`, which builds its own temp git
  repo). The operational reality — three quiet nights separated by two *repo
  commits* of `configs/calibration/calibration_ledger_head.json` — is never
  proven end to end.
- **G3. No NEEDS_SCOPE protocol.** The plan says "No production modules … or
  existing tests are in scope" but never states what the implementer does when
  the regression exposes a genuine U1/U2 defect (the likely outcome for an
  integration regression). U8's plan states this; U4's does not.
- **G4. `fixture_spec.json`'s role is undefined.** The plan lists its contents
  but never says whether it is *consumed* by the harness (authoritative) or
  merely *documentation duplicated in code*. If the latter, it can drift silently
  and is dead weight in the write scope.
- **G5. Test-double boundary is under-specified.** "the raw-physics refit is
  replaced with a deterministic test double returning each evidence file's exact
  decimal bound" — the plan does not name the seam (function/module) being
  doubled, so two implementers would double different things. It also does not
  state a guard that the double is *not* in effect for any test whose oracle is a
  bound value.

### (b) Correctness against the memo/decisions

- The memo's own hedge licenses the fix for G1: *"the ideal terminal sequence is
  85 **under the proposed three-receipt session model**"* (memo, §Synthetic
  three-window live-ledger regression). U1's landed model is a five-receipt
  model. The memo is superseded by the implementation it authorized; the plan
  should say so rather than route around the production writer to preserve a
  literal.
- The count-boundary test is arithmetically right and I verified it against
  D-116: issued corpus is 30 valid, threshold is 38, "eight further valid
  same-epoch observations would" trigger `corpus_doubles_from_19_to_38`. Three
  windows contribute 6 valid live observations → **36**. The plan's "extend with
  two further" reaches 38 correctly.
- The plan's synthetic issued acceptance artifact is built by *cloning the
  production artifact's numeric fields, swapping in 19 generated corpus
  identities "while retaining the original bound lexemes and arithmetic", and
  recomputing `derivation_sha256`*. That artifact's bound is **not derivable from
  its own prior set**. D-116 records that the real artifact was "Emitted
  deterministically (not hand-edited) from the historical-import finalizations."
  A hand-patched parent will either mask a U2 successor defect or force the
  staged successor tests to be written around the inconsistency.
- Everything else I checked (import exclusion, six-candidate universe, binding
  exactness, D-110 `max(observed_drift_s, 0.010818)`) matches D-110 cl.1/D-102
  pin 3 and D-116 as recorded.

### (c) Ratified invariants

Fail-closed: respected — every vector's oracle is a refusal, and the
re-chain-before-mutate discipline (`_rechain()`) is exactly right, since it
prevents "broken hash" from masquerading as "semantic refusal". Append-only
custody: respected — no ledger truncation outside explicit rollback vectors.
No touching real custody artifacts: **respected and load-bearing** — the plan
byte-authenticates the *real* issued artifact read-only (step 1) and does all
mutation on synthetic trees in tempdirs. Minimal additive edits: N/A (test-only
scope). No concerns here.

### (d) Test quality — one near-tautology, confirmed

- **T1 (blocking).** `test_d110_never_zero_allowance_is_embedded_once_in_all_three_verdicts`
  **cannot discriminate a broken implementation.** The fixture pins endpoint
  bounds alpha `0.025/0.026`, beta `0.027/0.028`, gamma `0.029/0.030` — every
  observed drift is `0.001`, and every one is below the `0.010818` screen. The
  applied allowance is therefore `0.010818` in all three windows, so the test
  passes identically against `max(drift, 0.010818)`, against the constant
  `0.010818`, and against `min(...)`. The one branch D-110 exists to protect —
  drift *above* the never-zero floor — is never taken.
- **T2.** `test_three_receipt_sessions_terminate_at_sequence_85` is
  construction-shaped: the plan chooses the API path that produces 85 and then
  asserts 85. It discriminates nothing about the path the operator will run.
- **T3.** Several universe tests ("supply the tuple", omit/add/duplicate) exercise
  the *guard on a caller-supplied candidate tuple*, not discovery. Only
  `test_candidate_discovery_never_invokes_loader_for_import_marked_observations`
  (a call-count spy — good design) is discovery-driven. There is no test proving
  the production path derives the universe from the snapshot without caller
  supply.
- Everything else is genuinely discriminating. The mutation-with-rechain
  discipline, the cross-window binding swap, the sibling-fork-with-valid-hash
  vector, and the T1-mismatch vector (internally consistent under a *different*
  T1) are the kind of vectors that catch real defects.

### (e) Scope discipline

Exhaustive and minimal, and **narrower than the memo** — the memo licensed
`tests/fixtures/calibration_live_three_window/**` (a glob); the plan commits to
exactly one JSON file plus one test module. That is the right direction. The only
scope defect is the missing NEEDS_SCOPE clause (G3).

### (f) What it misses that the register/memo require

- **M1. L5 by name.** The register: *"bracket selection can BORROW another
  window's receipts (global candidate scan; no runs_root/intended-pair binding)…
  U1 review MUST include this scenario as a regression vector."* U1's fix round
  added "L5 mandatory window/runs_root binding". U4 is the *integration*
  regression where three windows share one ledger — the exact topology L5
  described — yet no test names `runs_root`/`window_id` binding. The neighbor-
  substitution and cross-window-binding tests are adjacent but not the same
  assertion.
- **M2. No positive count-boundary oracle.** The operationally load-bearing fact
  is that the no-failure three-window campaign ends at **36 valid** — two short
  of the D-102 trigger. Nothing in the plan asserts this. It matters because any
  calibration retry, any fourth window (including Ed's optional 256-token prefill
  plan), or any extra fiducial crosses 38 and forces a successor mid-campaign.
- **M3. Per-window verdict issuance is never modelled.** Step 6 evaluates all
  three verdicts from a single sequence-85 (really 91) terminal snapshot. But the
  memo's §5A closing bookend runs *per window*: alpha's verdict is emitted at
  alpha's closeout, when the ledger holds only alpha's two live observations. The
  regression never proves (i) that alpha's verdict is issuable from its own
  terminal snapshot, nor (ii) that it remains re-verifiable at the campaign's
  terminal head after beta and gamma appended. If (ii) fails the campaign is
  broken and U4 will not have caught it.
- **M4.** No cross-window openness vector: beta's session left open while alpha's
  already-issued verdict is re-verified.

### U4 amendment list (paste-ready)

1. **Supersede the 85 oracle.** Build the fixture through the production writer
   path including `claim_bracket_session_slot` (as
   `scripts/validate_powermetrics_fiducial.py:409` does). Rename the test
   `test_three_windows_terminate_at_the_production_writer_sequence` and assert
   the derived value (3 sessions × 5 receipts = 15 → sequence **91**) *computed
   from a named module constant*, not a hardcoded literal. Additionally assert
   the two semantically load-bearing counts that are model-independent:
   `len(sessions) == 3` and `len(live_observations) == 6`. Record in
   `fixture_spec.json` that the memo's "85" is superseded by landed U1.
2. **Add a second, claim-free sequence variant only if the lead rules that the
   direct open/finalize path remains supported.** If it is not supported, delete
   the direct-API construction entirely; do not keep a fixture built by a path no
   operator will run.
3. **Make the D-110 allowance test discriminating (blocking).** Add a fourth
   synthetic window (or re-pin gamma) whose endpoint bounds give
   `observed_drift_s > 0.010818` — e.g. `0.029 / 0.045` (drift `0.016`). Assert
   `applied_allowance == observed_drift` on that window and
   `applied_allowance == 0.010818` on the sub-floor windows, in the same test, so
   `max()` is discriminated from a constant. Assert `embedding_count == 1` on
   both branches.
4. **Derive the synthetic acceptance artifact, do not patch it.** Emit it by
   running the same deterministic derivation used for D-116 over the 19 synthetic
   corpus members, so the synthetic parent's bound is reproducible from its own
   prior set. If that emitter is not importable within U4's write scope, raise
   `NEEDS_SCOPE` naming the emitter — do not ship an arithmetically inconsistent
   parent that the staged U2 successor tests must be written around.
5. **Run the whole happy path inside one temporary git repo with committed-pin
   enforcement ON.** Commit `configs/calibration/calibration_ledger_head.json`
   at each window boundary (mirroring the two real inter-night commits) and add
   `test_three_windows_require_two_intervening_committed_pin_advances` — a
   positive proof of the campaign's commit cadence, and the counterpart to the
   existing uncommitted-head refusal.
6. **Name L5 explicitly.** Add
   `test_candidate_under_another_windows_runs_root_cannot_bracket_this_window`:
   place a fully authentic, causal, same-epoch, fresh live observation under
   alpha's `runs_root` and attempt to bracket beta's science with it *absent* a
   binding (the original global-scan defect) and *with* a binding naming it.
   Both must refuse, and the refusal must cite the window/runs_root binding, not
   only the binding digest.
7. **Add the positive count-boundary oracle.**
   `test_no_failure_three_window_campaign_ends_at_36_valid_below_the_38_trigger`,
   asserting the trigger is *not* fired and that adding exactly two further valid
   same-epoch observations fires `corpus_doubles_from_19_to_38`. Comment the
   operational consequence (a fourth window or any calibration retry crosses it).
8. **Add per-window verdict issuance.**
   `test_alpha_verdict_issues_from_its_own_terminal_snapshot_and_re_verifies_at_campaign_terminal_head`
   — issue alpha's verdict at its own terminal head, then re-verify the identical
   verdict bytes against the campaign terminal snapshot after beta and gamma
   appended. Repeat for beta. This is the operational path; the single-snapshot
   evaluation is the memo's convenience, not §5A's procedure.
9. **Add cross-window openness.**
   `test_open_beta_session_does_not_invalidate_alphas_issued_verdict_but_blocks_a_campaign_terminal_pin`.
10. **Add a discovery-authority test.**
    `test_verdict_path_derives_candidate_universe_from_snapshot_without_caller_supply`
    — prove at least one production entry point does not accept a caller-supplied
    tuple, so the omit/add/duplicate guards are not the only universe defence.
11. **Name the doubled seam.** State the exact function being replaced by the
    deterministic bound-returning double, and add an assertion that the double is
    inactive in any test whose oracle is a bound/allowance value.
12. **Add the NEEDS_SCOPE clause:** "If the regression exposes a defect in U1/U2
    production code, early-return `NEEDS_SCOPE` naming the file and the failing
    vector. Do not widen scope, and do not weaken an oracle to make a test pass."
13. **Define `fixture_spec.json`'s authority:** it is *consumed* by the harness
    as the single source of the expected literals (sequences, counts, bounds,
    epoch, T1 vector); the test module must not restate any of them. Add
    `test_fixture_spec_is_the_sole_source_of_expected_literals` or drop the file
    from scope.

### U4 — three highest-risk gaps

1. **The regression will certify a ledger shape the three nights will not
   produce.** The plan routes around `claim_bracket_session_slot` to preserve the
   memo's "85". The production writer claims before finalizing, so the real
   campaign ledger interleaves claim receipts that U4 never exercises through
   discovery, binding, or verdict evaluation. This is the failure mode the whole
   unit exists to prevent, reintroduced by fidelity to a superseded literal.
   (Amendments 1, 2.)
2. **The D-110 never-zero test cannot fail.** Every fixture window has drift
   `0.001`, below the `0.010818` screen; the test passes against a hardcoded
   constant. D-110 cl.1 binds the never-zero allowance to *every mint under
   D-117*; U4 is where it is supposed to be proven, and as drafted it is not.
   (Amendment 3.)
3. **Per-window verdict issuance and the inter-night commit cadence are both
   unproven.** The plan evaluates from one terminal snapshot inside one process;
   the campaign issues three verdicts across three nights separated by committed
   pin advances. A defect in either — an alpha verdict that will not re-verify at
   the terminal head, or a pin-commit step that refuses — strands night two or
   three, which is exactly the charge the night-hardening register set.
   (Amendments 5, 8.)

---

# PLAN U8 — frozen-plan readiness validator + runbook §5A amendment

## Verdict: **REWORK**

The validator half is good work: the check table is comprehensive, the refusal
semantics are correctly fail-closed with no warning tier, the "no filesystem
writes / no repair" posture is right, the read-once-then-parse-and-hash-from-
captured-bytes rule closes a real TOCTOU class, and the plan directly and
competently closes the register's R6 (`readiness_launch_path_not_absolute` plus
a separate test for collection *and* whole-window verdict `--runs-dir`) and R7
(never-kill-verdict). The refusal to accept a self-declared acceptance JSON in
favour of U2's authenticated registry closes L4's core.

It is REWORK, not ACCEPT-WITH-AMENDMENTS, for three independent reasons, any one
of which is disqualifying:

1. The runbook amendment as specified **conflicts with four ratified sections of
   the document it edits** and violates the minimal-additive-edit invariant.
2. The plan **leaves the pre-flight calibration screen (§5B) untouched**, so the
   ratified runbook would carry two contradictory pre-science screens and a
   retry rule the frozen zero-retry ledger capability cannot represent.
3. The plan **is not executable**: it opens with "Begin implementation only
   after…" five unmet dependencies and closes with eight open questions, five of
   which are load-bearing design decisions (plan-tree contract, absolute-path
   syntax, fresh-root rule, reason-code closure, waiver canonical bytes). The
   charge's bar is "zero further design decisions." It fails that bar by its own
   admission.

### (a) Completeness — gaps

- **G1.** Five blocking dependencies (U1 final, U2 registry+probe, U5–U7 plan-tree
  and launch representation, reason-code unit landed, clean integration head) —
  of which U2, U5, U6, U7 do not exist and the reason-code unit is an *unratified
  candidate* (register: "Candidate small unit (U1.6) … Decide at the readiness
  gate"). Nothing in U8 can start.
- **G2.** Eight open questions, five design-bearing. Q2 (which artifact is the
  transitive hash closure), Q3 (literal argv vs expansion), Q4 (absent vs empty
  fresh root), Q6 (reason-code schema identity), and Q8 (waiver canonical bytes)
  each change the validator's code. Recommendations are offered but not ruled.
- **G3.** **The receipt has no custody destination.** The validator "performs no
  filesystem writes" and emits the receipt to stdout. Nowhere does the plan or
  the runbook amendment say where that receipt is written, that its SHA is
  recorded in §12 close-out, or that it is preserved as immutable window
  evidence. The PASS evidence for arming a claim window is, as drafted,
  ephemeral terminal output.
- **G4.** **The receipt is never bound to the arm.** There is no timestamp, no
  max-age/TTL, and no requirement that the bracket-session capability receipt
  record `readiness_receipt_sha256`. An operator can validate, then arm an hour
  later after any state change. The memo explicitly requires the opposite: the
  order manifest must carry "**arm-time attachment slots for the readiness
  record**, session capability, and actual receipt identifiers."
- **G5.** **The readiness record has no provenance requirement.** It is an
  arbitrary absolute path plus an operator-supplied `--expected-record-sha256`.
  Both are under the operator's (or an agent's) hand; regenerating the record and
  its expected SHA together passes. A fail-closed validator is only as strong as
  the provenance of what it validates.
- **G6.** Exit `2` is overloaded across malformed arguments, check failures, and
  "normalized internal refusal." The D-116 consumer gauntlet already caught
  "exit-3 masking" as a blocker; this reintroduces the class. An operator cannot
  distinguish a flag typo from "the machine is not ready."
- **G7.** The `readiness_*` code namespace (~30 new codes) has no declared home.
  `docs/phase_2/refusal_scope_spec.md` is "the ONE home for reason-code scoping";
  S2 defaults unknown codes to GLOBAL (safe), and S4 makes any S1 scope move a
  mandatory cold gate. The plan neither registers the namespace nor states that
  readiness codes are out of S1's domain. This is the register's URGENT "shadow
  taxonomy" defect, reproduced.
- **G8.** The validator runs at §5A step 1, *before* the clock/network-time step
  (step 4). Nothing re-verifies network-time-off, the settle, or absence of a
  pending time sync after that step. See M2 below.

### (b) Correctness against the memo/runbook/decisions

- **Divergence from memo §5A.** Memo step 3: *"Correct the clock against the
  trusted source, record the correction and `usingnetworktime` state, turn
  network time off, **and settle for at least 180 seconds**."* The plan's opening
  step 4 is "Correct the clock against the trusted source; record prior
  network-time state; disable network time" — the 180-second settle is **dropped
  from the ordered sequence**. The runbook's existing §5A does carry it ("Settle
  150–240 seconds — use 180"), and the memo's budget table states "The
  pre-calibration allowance includes the required 180-second post-admin settle."
  The plan's own ordering test ("readiness → ledger equality → clock → quiet idle
  → capability → pre finalization → successor probe → member one") would then
  *pin a sequence that omits the settle*, converting an omission into a ratified
  order.
- **Section collisions.** `docs/phase_2/window_runbook.md` already contains
  §5B "Pre-flight calibration screen (D-079 clause 3)" (:383), §8 "Check the
  fresh bound and calibration bracket" (:701), §9 "Emit exactly one whole-window
  verdict" (:737), §11 "Back up, then extract in the same custody session"
  (:911), §12 "Close-out record" (:946). The plan's "closing bookend" inside
  **§5A — a section titled "Pre-window clock stabilization"** — restates the
  normative ordering of §8, §9 and §11. Three duplicate normative orderings in
  one ratified operator document is a defect, not an amendment.
- **§5B is left standing and now contradicts the frozen design.** §5B:400-455
  (i) hardcodes the copied scalar `0.033558756679900` — precisely L4's defect,
  which the plan claims to close but does not touch, and (ii) ratifies a
  cause-removal retry: *"A retry is permitted **only** when a specific, named
  cause has been identified **and removed** … stay inside the retry count
  pre-registered in the frozen plan."* The memo forecloses this: *"Base plans
  should freeze calibration retry count at zero… If the lead wants one
  cause-removal retry, the session capability needs additional prospectively
  numbered slots and deterministic selection semantics before freeze — never an
  improvised retry."* A two-slot session **cannot represent** a second pre
  observation. As drafted, the runbook would give the operator written license
  to do something the ledger will refuse, at 2 a.m., mid-window.
- **The register's R5 is not addressed at all.** *"cooldown/cap arithmetic uses
  wall clock, not monotonic — network-time-off reduces but does not remove;
  register for the hardening unit."* U8 is the operator-procedure home the
  register nominated ("explicit operator-procedure mitigations"). No rule, no
  check, no test.
- **The reason-code gate is self-ratifying.** The plan makes an unratified
  candidate unit a hard blocking dependency and invents two refusal codes for it.
  Under rule 11 the lieutenant may not ratify a process rule or a mandatory
  trigger; the register says "Decide at the readiness gate."
- Everything else I checked against the memo's §5A bookends (steps 1, 2, 4–7
  opening; 1–6 closing) is faithfully represented, and the branch logic at
  opening step 9 correctly implements memo F3's three-way pre-science disposition.

### (c) Ratified invariants

Fail-closed: **respected and well done** — no warning tier, `REFUSE` on any unmet
check, "never 'approve' a mismatch through a waiver or manual edit", and an
explicit `--waivers`/`--environment-override` argv ban. Append-only custody:
**violated by omission** — the receipt has no custody destination (G3) and no
binding into the ledger or order manifest (G4). No touching real custody
artifacts: respected (temp trees, mocked probes, no production campaign in
verification). **Minimal additive edits to ratified docs: violated** — the plan
"amend[s] §5A into the complete per-window operator bookend", which is a
re-scoping of a ratified section plus three duplicated normative orderings. Note
the runbook already demonstrates the correct convention: it carries
`### D-100 §9 amendment — …` (:768) and `### D-100 §10 amendment — …` (:855) as
in-place additive amendment blocks. U8 should use it.

### (d) Test quality

- **Strong and discriminating:** "Validator performs no filesystem mutation"
  (tree-hash before/after is a real property); the path-form matrix (relative,
  `~`, `$RUNS_ROOT`, `${...}`, `..`, symlink, FIFO/device, aliasing, ancestor
  overlap); "Verify bytes are hashed and parsed from one captured read" (this is
  the TOCTOU oracle and it is exactly right); the **race regression** ("readiness
  passes, another writer claims the ID, then U1's atomic reservation still
  refuses") — that is a genuinely sophisticated vector; "Self-consistent but
  unregistered successor refuses"; "Live or stale `campaign.lock` refuses
  readiness; validator does not delete it."
- **Near-tautological as specified:** the four "Runbook contract checks" are
  substring/ordering greps over prose the same implementer writes in the same
  commit. They have regression value (a future editor deleting the never-kill
  rule) but zero present discriminating value, and the ordering test is only
  meaningful if it parses structure rather than searching for index positions.
- **Missing entirely:** no test that the receipt is custodied; no test of receipt
  freshness/TTL; no negative test that a hand-authored readiness record (correct
  self-SHA, not derived from the frozen plan tree) is refused; no test of the
  180-second settle; no test that exit codes distinguish usage error from
  REFUSE; no test that a *passing* readiness receipt is required before the
  bracket append.

### (e) Scope discipline

WRITE_SCOPE matches the memo's U8 row exactly (three files) and the exclusion
list is exemplary — it names `scripts/prewindow_check.sh`, ledger/bracketing
modules, successor machinery, acceptance registry, reason-code producers, packs,
state files, run reports, and forbids new committed fixtures. The NEEDS_SCOPE /
NEEDS_RULING early-return clause is present and correctly phrased ("do not weaken
U8"). **This is the best-scoped part of either plan.** The problem is not scope
breadth; it is that three obligations the plan accepts (reason-code registration,
§5B reconciliation, receipt custody binding) fall *outside* those three files and
are neither NEEDS_SCOPE'd nor deferred to a named owner.

### (f) What it misses that the register/memo require

- **M1.** L4's second half — *"de-duplicating the hardcoded literal"* — is
  untouched (`0.033558756679900` in §5B:406 and its `0.01` policy-JSON twin from
  the paper-fidelity queue). Outside scope, but must be NEEDS_SCOPE'd with an
  owner, not silently dropped.
- **M2.** R5 (wall-clock vs monotonic cooldown) — no operator mitigation.
- **M3.** The memo's order-manifest requirement for "arm-time attachment slots
  for the readiness record" — the plan emits a receipt that attaches to nothing.
- **M4.** Memo closing step 6 requires the network-time restoration be *recorded*;
  the plan restores it but adds no §12 close-out field.
- **M5.** §5B's retry rules vs the frozen zero-retry policy (see (b)).

### U8 amendment list (paste-ready)

1. **Restructure the runbook edit as additive amendment blocks, following the
   document's own convention.** Do not re-scope §5A. Instead add:
   `### D-117 §5A amendment — frozen-plan readiness gate and two-slot bracket
   capability` (opening bookend, inserted before the existing clock subsection,
   which is retained verbatim); `### D-117 §5B amendment — zero calibration
   retries under the two-slot session`; `### D-117 §8 amendment — terminal head
   pin and bracket binding from one immutable snapshot`; `### D-117 §9
   amendment — never kill a running whole-window verdict`; `### D-117 §11
   amendment — absolute-path mandate for backup and extraction`. No normative
   ordering may appear in two sections.
2. **Reconcile §5B or stop (blocking).** Amend §5B to state: the pre-flight level
   screen is superseded by the U2 pre-science acceptance + D-102 trigger probe;
   **calibration retry count is zero**; a failing pre observation triggers
   governed abort of the bracket session and ends the window; §5B's cause-removal
   retry paragraph is retired for D-117 windows because the two-slot capability
   cannot represent a second pre observation. If the lead has not ruled the
   zero-retry policy, early-return `NEEDS_RULING` — do not ship a runbook that
   licenses an unrepresentable operator action.
3. **Restore the 180-second settle as a numbered step** in the opening bookend
   (between "disable network time" and "establish zero-agent state"), citing the
   existing §5A text and the memo's budget line, and include it in the frozen
   ordering tuple asserted by the ordering test.
4. **Custody the receipt (blocking).** Runbook must specify the exact absolute
   destination under the window's operator-log root, that the operator records the
   receipt SHA-256, and that §12 close-out carries a `frozen_plan_readiness_receipt_sha256`
   field. The validator still performs no writes; the *runbook* owns the
   redirection and the hash record.
5. **Bind the receipt to the arm (blocking).** Add `generated_at_monotonic_s` and
   `generated_at_wall_s` to the receipt, define a max-age (recommend 30 min), and
   require the bracket-session capability receipt to carry
   `readiness_receipt_sha256`. The capability field is U1's — raise `NEEDS_SCOPE`
   naming `joulewise/calibration_ledger.py` rather than dropping the binding.
6. **Require readiness-record provenance.** The record must be a repository
   artifact committed at `reviewed_git_commit`, and its SHA must appear in the
   frozen plan-tree manifest. `--expected-record-sha256` then cross-checks a
   *reviewed* value rather than an operator-chosen one. Add
   `test_readiness_record_absent_from_plan_tree_manifest_refuses`.
7. **Split exit codes.** `0` = PASS; `2` = REFUSE (receipt always emitted); `64` =
   usage/malformed-arguments (no receipt). Add
   `test_usage_error_and_refuse_have_distinct_exit_codes` and
   `test_refuse_always_emits_a_receipt_on_stdout`.
8. **Declare the `readiness_*` namespace.** State explicitly in the script
   docstring and the runbook amendment that readiness codes never enter a
   window-verdict reason container and are therefore outside
   `refusal_scope_spec.md` S1's domain; enumerate them in one module-level frozen
   tuple with a test that the emitted set equals that tuple. If the lead instead
   wants them in S1, that is an S4 mandatory cold-gate trigger — flag, do not act.
9. **Make the reason-code gate conditional, not self-ratified.** Implement the
   check behind a single named module constant (`REASON_CODE_GATE_REQUIRED`,
   default **False**) with a `COLD-GATE` comment tag, so the lead's ruling at the
   readiness gate flips it in a one-line diff. Record in the plan that the
   register calls this an unratified candidate unit (U1.6).
10. **Add R5 operator mitigation.** Runbook rule: automatic network time stays off
    for the entire window, no manual clock change occurs between arm and
    close-out, and any clock adjustment during a window invalidates the window's
    cooldown/cap arithmetic (wall-clock based) and is a close-out deviation. Add
    a post-clock re-verification step (validator `--phase post-clock` or an
    explicit operator-confirmed field) covering `usingnetworktime == off`, the
    settle having elapsed, and no pending time sync.
11. **Record the L4 literal de-duplication as a NEEDS_SCOPE deferral with an owner
    and a target unit** (the `0.033558756679900` copy in §5B and the `0.01`
    policy-JSON twin). Do not let it fall between U2 and U8.
12. **Turn the runbook contract tests into structural tests.** Give each ordered
    step a stable anchor ID in the markdown (e.g. `<!-- step:5A.7 -->`), parse
    the §5A amendment into a step-ID tuple, and compare against a frozen expected
    tuple in the test. Substring greps for prose are acceptable only for the four
    prohibition rules.
13. **Add the missing negative tests:** hand-authored record not in the plan tree
    refuses; stale receipt (age > max) refuses at arm; bracket append without a
    referenced readiness receipt refuses; ordering tuple missing the settle step
    fails.
14. **Resolve open questions 2, 3, 4, 6, 8 before implementation starts.** Ship
    the plan's own recommendations as the default rulings (they are sound: one
    strict tree manifest per pack; literal absolute argv; nonexistent mutable
    roots; hashable reason-code schema id; canonical `[]\n` bytes) but obtain the
    lead's ratification — the plan may not ratify them itself.

### U8 — three highest-risk gaps

1. **The runbook amendment would put contradictory normative instructions in a
   ratified operator document read at 2 a.m. before a claim window.** §5B still
   licenses a cause-removal calibration retry that the frozen two-slot session
   physically cannot represent; §8/§9/§11 orderings would be restated inside a
   section titled "Pre-window clock stabilization"; and the memo's mandatory
   180-second post-admin settle is dropped from the very step sequence the plan
   asks a test to freeze. The failure mode is not a broken build — it is an
   operator following the document and stranding a night.
   (Amendments 1, 2, 3.)
2. **The readiness gate is unbound and uncustodied, so it can be satisfied
   without being true.** The record's provenance is operator-supplied, the
   expected SHA is operator-supplied, the receipt is written nowhere, it carries
   no timestamp, and nothing in the ledger references it. Every individual check
   in the table is fail-closed; the *gate as a whole* is not, because the object
   it validates and the evidence it produces are both outside custody.
   (Amendments 4, 5, 6.)
3. **U8 cannot be implemented and the plan says so.** Five unlanded dependencies
   (two of which — U5–U7 packs and the reason-code unit — do not exist even as
   ratified work) and five unruled design questions. Sequencing this unit now
   spends a Sol session producing a validator against an invented plan-tree
   contract that U5–U7 will then have to match, inverting the dependency the memo
   set ("U8 … After U1, U2, U5–U7"). The right next action is the two rulings
   (zero-retry, reason-code gate) plus the U5–U7 plan-tree/launch-manifest
   contract — not U8 implementation.
   (Amendments 9, 14.)

---

## Cross-cutting note for the magistrate

Both plans inherit the same structural weakness: **they treat the design memo's
literals as frozen after U1 has already superseded some of them.** U4's "85"
is the visible case; the memo's F1 wrote a three-receipt model, and landed U1 is
a five-receipt model with exclusive slot claims. Any downstream unit that pins a
memo literal without re-reading the branch will encode the same staleness. The
cheap systemic fix is a rule for the remaining plan-factory drafts: *every
numeric or structural oracle taken from the memo must be re-derived from the
landed branch and the divergence recorded in the plan.* That rule would also have
caught the §5B retry contradiction in U8.
