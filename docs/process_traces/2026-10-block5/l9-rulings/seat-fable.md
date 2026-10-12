# Lane L9 consult, Fable 5.1 seat (blind)

Read-only. Working tree `3c05b8076`; design `L9_DESIGN.md` SHA-256 `3465acf9…2e7d` (recomputed). Pinned
source read with `git show b039c0257:` (two scratch copies under `/tmp`, deleted at the end). Nothing executed
beyond `git show`, `shasum`, `grep` and `sed`. No path under `night-custody`, `night-b5`, `night-g2a` or
`harvest-v5-b5-*` was opened; no `derived/`, `sources/` or `withheld/` of any attempt; no RUN_STATE, CLAUDE.md,
orchestration doc or decision log. Every number below is made up and says so. Line numbers are main unless
marked `@pin` (`b039c0257`); "WW" is `joulewise/whole_window.py`, "RC" is `scripts/run_campaign.py`, "H" is
`joulewise/b5/harvest.py`.

---

## Q1 (O2): a row the validator admits that should not bear a number

**Answer.** Under the design as written I found no such row, and I can say why: of the member family, the only
stored condition the mechanism can actually set aside is `whole_window_bundle_invalid`, and for that one the
pinned harvest's own reproduction check (recorded sources) or basis check (catalog path) guarantees that an
excluded reference's energy is in no allowance. But the table's clause "or is a NEG-8 reference or spare" is
written for all thirteen member reasons, and it is wrong for the twelve that name an *included* member: those
members' energies are in the stored bracket and the harvest does not lose a reference for any of them. The
design does not notice this because it answers *conditions*, while the validator re-derives those twelve
failures as *reasons* outside the conditions list, so today they refuse regardless. The moment S3 makes the
member level real (which section 3.5 promises and which the validator as described does not deliver), the
clause produces the row below. The finding does not depend on J1's outcome except trivially: under position A
nothing in the family is set aside and the row refuses, along with every window that has one such member.

**The row (construct it from the writer; every value made up).** A BETA window whose start reference S2 ran
to completion: `summary_metrics.json` status `succeeded`, strict validation clean, custody triangle agrees. Its
pre-run idle admission recorded a CPU busy ratio above the criterion (or the GPU idle check `flagged`, or the
member's own records show thermal pressure `heavy` inside its measured window).

- *Writer.* S2 is `usable` (RC 455 to 482: status, strict, no collection flag), so it is in `bundle_ids` and in
  the basis, and it is one of the `included` evaluations handed to the core (RC 8399, 8468). The core appends S2
  to `neg8_references["start"]` unconditionally (RC 7205 to 7215: the admission branch and the reference branch
  are independent) and puts `cpu_busy_ratio_p95_exceeded` (or `gpu_idle_admission_not_passed`, or
  `thermal_pressure_elevated_in_window`, RC 7081 to 7140 and `environment_admission.py` 265, 450) into
  `conditions` and a `member_failures` record naming S2. The stored bracket's start mean contains S2's energy;
  status `failed`.
- *Harvest at the pin.* S2 gets `member.whole_window_member_failure` (H@pin 752 to 758 lists all eleven
  admission reasons; 4926 to 4960 emits it; the catalog makes it EXCLUDE_MEMBER, `flag_catalog.json` 801 to
  806). That code is **not** in `NEG8_REFERENCE_LOSS_CODES` (H@pin 92 to 131: physics, reference-physics,
  timeout, admission-aborted, strict, member-validity, model identity). `_neg8_reference_losses` (H@pin 5133 to
  5230) therefore names no loss for S2; the re-screen's reproduction pass matches the stored bracket (S2 in
  both) and the exclusion pass keeps S2 (H@pin 5495 to 5525). S2 is a reference, not a unit, so no cell count
  moves. Result: `claim_usable` true, allowance record `survivor_rescreen`, S2's contended energy inside the
  start mean that sets the drift allowance. For the thermal variant note that the harvest's
  `thermal.powermetrics_pressure_elevated` is the monitor's reading while the writer's reason is from the
  member's own records; they can disagree, and only the monitor's loses a reference.
- *Design's validator with the context.* The `neg8_*` conditions are answered by the allowance record. The
  stored member reason names S2, S2 "is a NEG-8 reference or spare": answered (table row 4). `claim_licensing`
  true. If S3 also scopes the three re-derived member checks (below) by the same clause, the row is admitted and
  `E_whole_window_drift_allowance_j` (half the gross allowance, `inputs.py` 4030 to 4038) enters B of every
  reported cell of the window and D of both contrasts if the window is GAMMA (plan 240 to 246; 7.1 step 5), and
  the floor's allowance through J5. That is a number the registration says a contended reference may not set
  (H@pin 100 to 104 states the hazard in its own words).

**Why the design as written still refuses it, and why that is not a defence.** The validator re-derives the
twelve included-member failures as reasons, not as conditions: environment and thermal at WW 5340 to 5346
(`current_environment_refusals`, which contains `_window_thermal_pressure_refusals`, `environment_admission.py`
255 to 270), the CPU decision of every stored member at WW 6935 to 6950 and its mismatch at 5390 (a decision is
`failed` on any threshold condition, `idle_admission.py` 455 to 470). Section 4.5 Change 2 lists "CPU admission
of the stored members, unchanged" and says nothing about 5340. So: (i) table row 4 is dead code for the twelve
reasons; (ii) a window with one included science member carrying any of them is refused whole, which is exactly
the window-level reach registration 6.5 (4097 to 4105) removed and the design claims B restores; (iii) the only
fixtures named (`…_WRITER_DROPPED_SCIENCE_MEMBER`, `…_WRITER_DROPPED_REFERENCE`) are *excluded*-member cases
(`whole_window_bundle_invalid`), so no S3 test touches the live question. The plan's own forcing problem for the
sensitivity line (529 to 531: thermal removals expected "most of all on 8B prefill-p2048 members") makes case
(ii) likely on BETA and GAMMA. An implementer who closes (ii) in the obvious way, by scoping 5340, 5390 and
6935 with the table's clause, builds the row above. The clause must therefore be narrowed before S3, not after.

**What I checked for the items the brief lists.**

- *Cache (WW 6210 to 6257).* Keyed on row hash, runs root, referenced ids, basis digest; stored on the session
  object; only admits are cached (6249). Safe while one session carries one frozen context. Two exposures the
  design should state: the sensitivity pass (4.13 part 3) takes `contexts` as an argument and must build a new
  session per context, never reuse a primary session whose cache holds an admit; and `member_scope` is read
  into the answered set, so a session must not outlive a change of that flag (tests that flip it in-process
  would otherwise read a stale admit).
- *`archive_context=None`.* With `context=None` the design keeps `row.status == "passed" and
  bracket.decision == "passed"` (WW 6756 to 6757) and the conditions test (5401 to 5403). I see no path in 4.5
  that changes a default; the harvest's calls (H@pin 5505) pass no context. Not verified by execution.
- *A member reason naming a reference or spare.* The admitted row above (included reference). For an
  *excluded* reference under `whole_window_bundle_invalid` the clause is justified: on recorded sources the
  harvest's reproduction pass reads every invoked reference of the manifests (`_derived_neg8_decision`, WW 4895
  to 4990; H@pin 5500 to 5520 with `unlisted_strict_invalid="read"`, `unreadable_energy="writer_entry"`) and
  requires `_neg8_reproduces` against a stored bracket built from `included` only (RC 8468), so a reference the
  writer dropped on a ground the harvest lacks (the collection flags of RC 397 to 404, 2919 to 2934: prompt hash,
  config-manifest mismatch, anchor fallback) changes the start or end mean and fails the screen; on the catalog
  path item 7(b) requires every survivor to be a basis occurrence (H@pin 5287 to 5315), and the basis is built
  from `included` (RC 8521 to 8524). Either way such a window is not claim-usable, so no analysed window has it.
- *Erratum 2 item 9 replay in place of the membership check.* Two gaps, both refusals rather than admits, but
  both would make the catalog path yield nothing unless S3 decides them: (a) with an empty source list the
  validator's `verified_source_manifests` is empty, and `_current_core_rederivation_reasons` (WW 5253 to 5330)
  then has `paths is None` and refuses, so S3 must feed the authenticated catalog's manifests into the core
  re-derivation and the launch check, not only "take the two checks as made"; (b) 4.5 Change 2 lists "the
  replay of the stored NEG-8 bracket, unchanged", but on this path the stored bracket is `missing` (Erratum 2
  item 7: "the stored-bracket comparison cannot be made") and WW 6790 to 6900 would conflict against the
  catalog's references; the design must say the withheld re-screen bracket's equality, which the replay already
  checks, stands in for it. Science members' membership is then checked only by the basis hashes
  (`_validated_evaluation_basis`), which is the row's own list; the tripwire `kept_member_outside_verdict_membership`
  covers the direction that matters (every kept member is in the row), and the reverse (a stray member in the
  row) bears no number because kept units come from the roster (3.4 check 7).
- *A condition the table does not name.* Falls to "anything else: refused"; correct. One mislabel inside the
  table: `adapter_continuity_failed` at WW 5416 is a *mismatch* between the stored continuity record and the one
  re-derived from the bundles (provenance), while 6920 is the *decision* not being `stable`. Registration 4159
  to 4160 makes the decision disclosed-only; it does not license accepting a stored record that the bundles do
  not reproduce. Set aside 6920 only.

Not verified: that the writer's `included` list is the one both the basis and the core see on the real block-5
chain (read from RC 8399 to 8524 only); that `_neg8_reproduces` compares the endpoint means (docstring at H@pin
5395 to 5410, function not read).

---

## Q2 (O6): the unreadable historical capture at finalization

**Answer.** Safe, with three things kept. Confirmed that finalization stops today: `analysis_manifest_v3.py`
3649 to 3662 loads the snapshot with `verify_custody=True`, `mode="read_replay"`, and any refusal becomes
`analysis_finalization_ledger_head_mismatch`; the custody pass (`calibration_ledger.py` 2688 to 2715 →
`_custody_reasons` 2396 to 2414 → `calibration_custody_worker.observation_custody_reasons`) returns the single
code `calibration_ledger_custody_invalid` on the first observation whose file is missing, unreadable **or
differs**, and stops at that observation. The case an unreadable capture could hide: a historical capture whose
bytes were altered and then evicted or made unreadable. That cannot change a number of this block, because no
block-5 consumer reads a number from a historical capture's files: the per-capture bound is in the ledger row
(`LedgerObservation.exact_bound_lexeme_s`, `calibration_ledger.py` 378), so B_max (Erratum 3 item 14) and the
bracket's range, doubling and systematic triggers are computed from rows, and the acceptance's screens are
numbers in the committed acceptance artifact. What must be kept:

1. The chain, the pin and the baseline-in-chain test (2654 to 2686) unchanged; the ledger is the archive's
   prefix (design 4.9, 4.13), so nothing appended later can matter.
2. Byte verification of the window's own two captures (the session's slots), and of any capture any block-5
   consumer reads a value from. Add a one-line test: the input census lists no file under any historical
   capture's `custody_locator`.
3. The relaxation must use the artifact-aware outcome (`_historical_custody_outcome`, 6592 to 6650:
   `changed` / `unreadable` / `absent` / `absent_or_unreachable` / `verified`), never a wholesale
   `verify_custody=False`. A present file whose digest differs (`changed`) must still stop: it is evidence that
   the ledger's recorded evidence was altered after the fact, which the registration treats as window-removing
   when relied on (4418 to 4423). Only `unreadable`, `absent` and `absent_or_unreachable` become the recorded
   flag, and the flag should carry the capture ids and be compared with the harvest's
   `derived/historical-custody.json` (a capture that verified at harvest and is unreadable now hides nothing;
   one that was unmeasured at harvest never verified and the record should say so).

Not verified: whether `probe_custody` in `read_replay` mode maps the custody locator to a backup root that the
archive holds (docstring 2520 to 2535 says replay maps backup roots); `_observation_custody_reasons` was read
through the worker only.

---

## Q3 (O13): the load-correlated sensitivity line for a contrast

**Answer.** The plan supports the design's reading, by two sentences: "the same estimator is recomputed … and
printed beside the primary value" with the form "(n = …)" for a contrast, and "It never replaces the primary
value, never gates anything and licenses no claim" (529 to 536). A Holm test, a floor decision or an outcome
word would be a gate or a claim; the registered battery-assist contrast line (558 to 561) is the precedent for
"§7.1 steps 1–4 (dbar and its metrology interval)". For reported cells, m, h and the counts match the plan's
worked example (half-width printed). Three things a reader needs that the design does not say:

- *A unit removed by a load-correlated code and another code.* The plan says it stays removed (532 to 534). The
  trigger ("when any unit … was removed by one of the three codes") can then fire with nothing restored, and the
  line would repeat the primary. Say whether the line prints (with "no unit restored") or is omitted; the plan's
  only omission rule (536) is for a unit removed by a non-load-correlated code alone.
- *Which units were restored.* The battery line prints the count of assist members per stratum; this line
  prints only n. Print the restored count per stratum (or per contrast) and the code families, as the kept-units
  disclosure does; without it the reader cannot tell a 9-quad line from a 10-quad one that restored nothing.
- *The decision interval.* "The same estimator" for a contrast includes step 5 (D over the restored quads). The
  design follows the battery precedent (steps 1 to 4). Either is defensible; the addendum must say which and why,
  because a reader comparing the line with the primary decision interval will otherwise supply D themselves.

Floor cells: the plan's "cell" includes floor cells (section 0 of the design; plan 2.2 and 6.6), and the form
"(n_r = …, n_b = …)" fits a floor cell with one stratum, so the text does not settle "no line". The forcing
problem (bias of a mean) argues for the design's choice. Record it as a reading in the addendum; it changes no
number.

---

## Q4 (open): the likeliest silent wrong number, and the cheapest check

**Answer.** Every first-kind timing bound, and with it B of every reported cell, the attribution floor, and the
comparative floor's shared-edge sweep, computed under the pre-capture bound instead of the window's operative
bound b_op, on the governed windows. Nothing refuses: the stored summary is authentic, the bound formula is
monotone (plan 246: the stored summary "was reduced under the pre capture's fiducial bound alone"), and the
value is simply smaller (made-up scale: pre 28.0 ms against b_op 45.0 ms moves a bound of 2.36 J to about
1.5 J). The path crosses three owners and the design says it was not traced (9.1 item 1).

**Evidence.** The re-reduction happens only inside the consumption session's `_prepare` (WW 653 to 880): it
takes the bound from its *own* `calibration_bracket_for_bundles` call (707, 738), and it returns stored
summaries without re-reducing in two branches: a MINTED-semantics session with no basis binding (694 to 705)
and any MINTED-semantics session (750 to 758). Re-reduction runs at 861 only on the MAX_BRACKET path when
`operative_bound > the member's own verified bound` (846). Block-5 rows read as MINTED semantics unless the
writer was told otherwise (`_row_consumption_semantics_id`, WW 5517 to 5530; RC 814 to 821 default); the
consumers default their sessions to MAX_BRACKET (`floor_extraction.py` 2870 to 2878; `mint_floor_artifact.py`
453 to 461) but `inputs.py` 3361 and 3434 pass through whatever `consumption_semantics_id` the caller gives.
Design 4.13 part 2 says the session's bracket evaluation "is replaced by the context's" and 4.2 says the first-kind
bound comes from `summary_for`, but neither says that `operative_fiducial_bound_s` (760) and the `dominated`
loop (846 to 880) must be driven by `window_bracket["b_fiducial_s"]`, nor which semantics each block-5 session
is built with. On a governed window the stored basis has no calibration pair (Erratum 3 item 9), so
`_basis_bracket_binding()` is None and the 694 branch is reachable. S8's test ("a made-up member whose stored
summary was reduced under one bound and whose window's operative bound is larger") catches a reader of the
stored summary only if it goes through the real session on a governed-shaped row; the design does not say it
does. Step 2's re-reduced summaries are, by the design's own table (2214), read by no later step, so they are
not a cross-check.

**Cheapest check.** The session already records `minted_fiducial_bound_s` and `operative_fiducial_bound_s` in
each member's consumption provenance (WW 932 to 937), and the claim gate copies that provenance onto the
evidence (`inputs.py` 3462 to 3468). Two assertions, one fixture property: (1) every S0 synthetic window has
b_post − b_pre equal to a marker (made up: 7.331 ms), so `dominated` is true for every member and b_op is
distinguishable from b_pre; (2) the extractor, the mint and the issuer refuse any kept member whose
`consumption_provenance.operative_fiducial_bound_s` is absent or differs from the context's
`window_bracket["b_fiducial_s"]`, and S8's test asserts the issued `E_clock_anchor_shift_bound_j` of one kept
member equals an independent `reduce_bundle(path, _authenticated_fiducial_bound_override_s=b_op)` (`reduce.py`
2715 to 2745) and differs from the stored summary's. That is one refusal code and one test, and it pins the
bound to the bracket by value on every real cell.

Not verified: which semantics the block-5 arm chain passed to `--whole-window-verdict` (no caller outside the
writer was found by grep; the pack's launcher is not on main's `scripts/` under that flag name).

---

RECOMMENDATION: Before S3 is written, narrow table row 4 of section 3.5 to two rules and make the validator's
re-derived member checks obey the same rules, because that is where the member level actually lives:
`whole_window_bundle_invalid` is answered when every member it names is in `removed_bundle_ids` or is a NEG-8
reference or spare (justified by the harvest's reproduction and basis checks, cite H@pin 5500 to 5525 and 5287
to 5315); every other member reason is answered only when the member it names is a science member in
`removed_bundle_ids`, and the corresponding re-derived reasons at WW 5340, 5390 and 6935 are suppressed for
exactly those members and no others; a reference or spare named by any of the twelve included-member reasons
refuses the window with a new code (`reference_failed_admission_in_screen`), because the harvest's screen used
its energy. Add the fixture `…_INCLUDED_REFERENCE_ADMISSION_FAILED` (admitted must be false with and without
`member_scope`) and `…_INCLUDED_SCIENCE_MEMBER_ADMISSION_FAILED` (admitted under B, refused under A). Split the
adapter row into 5416 (keep) and 6920 (set aside). In 4.5 Change 3 state that the catalog's authenticated
manifests feed the core re-derivation and the launch check, and that the withheld re-screen bracket's equality
replaces the stored-bracket replay on that path. State that the sensitivity pass builds one new session per
context. For O6, relax only the artifact-aware `unreadable`/`absent` outcomes and keep `changed` a stop, with the
census test that no historical capture file is read. For O13, add the three sentences of Q3. And give the
operative bound an owner: specify that every block-5 session is built with MAX_BRACKET semantics, that
`operative_fiducial_bound_s` is `window_bracket["b_fiducial_s"]`, that fixtures have b_post ≠ b_pre, and that
each consumer refuses a kept member whose provenance bound differs from it; without that, the design's most
likely wrong number is one no gate in it would see.
