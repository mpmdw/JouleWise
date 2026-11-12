# Block 5, from release to paper: synthesized audit (2026-11-07)

**What this is.** A synthesis of two independent audit seats, Fable 5.1 (seat 1) and Opus 5.5 (seat 2), on the
track "Block 5 release-to-paper path". The synthesis seat is Opus 5.5. I re-checked every claim kept below against
the repository, and both seat reports are reproduced verbatim in the appendix.

**Brief.** The audit covers everything after the unseal of Block 5 (analysis tag `b5/analysis-r3`; r4 in progress):
- the lean release runbook and `scripts/release_b5.py`;
- the results-fill, claim-rendering and paper-custody code;
- the Paper 1 drafts;
- how registered claims map to printed sentences and numbers.

The questions were: which steps are missing, manual or fragile; which claims are not mechanically bound to the
released record; where a human could unblind early; and what the paper says that the registration does not license.

**Evidence base.**
- `origin/main` at `bd7a3efcd`. The seats read `16c37a4bf`. The two later commits touch only `RUN_STATE.md` and a
  handoff note, so every other cited file is byte-identical at both commits. `RUN_STATE.md` lines are re-located to
  `bd7a3efcd`.
- Unmerged lanes, read with `git show`:
  - `lane/2026-10-27-paper1-draft` at `a1a5029fb` (no PR);
  - `lane/2026-11-05-b5-results-renderer` at `15dd5c8f7` (draft PR #652);
  - `lane/2026-11-05-b5-release-runbook` at `08fe9e6cf` (draft PR #648);
  - `lane/2026-11-05-b5-release-readiness` at `836548931` (draft PR #655).
- Citations are `path:line` at `bd7a3efcd` unless another commit is named. Paper 1 lines are `docs/paper/paper1/paper1.md` at
  `a1a5029fb`.

**Blinding.**
- No custody, archive, `night-*`, `jw-b5-*` or `restricted/` path was listed or opened.
- No Block-5 value, difference, verdict or outcome word was read or inferred.
- Structural statements already in the deviation log are quoted as written, and nothing is inferred from them.
- Nothing was run against data. No test was run; this is a reading audit.

---

## Executive summary

1. **The pre-unseal check is sound; almost nothing after it is written down.** `release_b5.py` (DLE-1) is tested and
   well guarded. After it prints `agree`:
   - the runbook ends at "Ask Ed for the unseal OK";
   - the seal record's "Release event" section is empty;
   - no Block-5 Results renderer is on `main`. The only one (#652) is unmerged and refuses DLE-1 custody;
   - Paper 1 is unmerged, and no program fills it.

   Today every printed number would be copied by hand from restricted JSON.
2. **The release condition cannot express a registered null outcome.** The comparator marks any null as DISAGREE,
   even when both sides are null, and it compares floor values whatever the resolution status. So a legitimate
   not-estimable contrast, or a refused floor resolution, can never reach `agree`. The plan says such an outcome
   "is the result and is printed as such". A blind rule is needed before r4 releases, whatever r4 turns out to be.
3. **Every remaining choice must be made before the release event, because the lead stops being blind at the
   event.** Ed's delegation of preregistration rulings covers blind rulings only. These are all still open:
   - placement (registration §14 Q4), and replacing the D-174 fallback disposition;
   - the gate that replaces the "Results cold gate", which DLE-0 abolished but Q-RENDERER still requires;
   - print precision;
   - the paper-input route;
   - independent hand-check sources for the seven families the recompute does not cover;
   - the analysis-program addendum of registration §11 item 4.
4. **There are concrete early-unblinding and stop-being-blind channels:**
   - an ordering gap: the runbook treats Ed's OK as the boundary, but the registration makes the recorded event the
     boundary;
   - `*.released.txt`, which holds values, sits beside `*.unreleased.txt`;
   - the public verdict's per-family pass counts, which include rows created per quad that raises the
     leave-one-out magnitude trigger;
   - the repository is public, so a released number committed anywhere unblinds the blind repair seats the plan
     relies on.
5. **Several Paper 1 sentences contradict the record:**
   - the registered tolerance;
   - when the analysis ran under DLE-1;
   - who could touch the data;
   - when the outcome text was fixed;
   - how a changed file is handled;
   - "every printed quantity" recomputed.

   They need fixing before any number enters the paper.
6. **The ordered checklist in §5 turns the path after unseal into copying only.** Most of it can run blind, in
   parallel with the r4 dry run. It covers: rulings, building the renderer and filler, a synthetic dress rehearsal,
   the release check from the tag, the release event committed before anyone reads, a frozen `SHA256SUMS` bundle,
   mechanical rendering, the hand check, the gate, the licence lint, and the fill.

---

## Decisions needed from the lead (all blind, before the release event)

1. **The release comparator and registered null states (blocks a legitimate release).** Decide whether a contrast
   or floor resolution in a registered null state can ever reach `agree`. Evidence: §2 A4.
   - **Recommended.**
     - For `not_estimable`, both programs already derive the word independently (`threshold_free`,
       `scripts/compare_b5_recompute.py:2507-2509`). So compare the word plus null-ness, and skip the numeric rows,
       with the bars unchanged.
     - For a refused floor resolution whose reason is the registered `floor_transport_inapplicable`, check
       transport applicability from the sealed manifest.
     - A binding or authentication refusal stays a hold traced blind, as DLE-3 already rules for D5
       (`docs/analysis/b5/DEVIATION-LOG.md:325-347`).
   - **What it takes.** A DLE entry; synthetic fixtures in each D-190 state; a cited rebind of the release-check
     commit.
   - **The alternative.** Rule that any null holds. Then say so in the deviation log, because it contradicts plan
     §3.1 (`configs/campaigns/v5_claim_25g83/analysis_plan_block5.md:178`).
2. **DLE-4: the gate that replaces the "Results cold gate".** The Q-RENDERER obligation still requires a renderer
   written after release to pass "the Results cold gate" (`docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md:631-638`),
   but DLE-0 abolished that gate (`DEVIATION-LOG.md:38-64`).
   - **Recommended.** One fresh executing reader:
     - re-runs the renderer's `--validate-rendered`;
     - samples leaves against the frozen bundle;
     - runs the licence lint (§2 B7);
     - checks the paper against §2 D.
   - That seat becomes the second licensed post-event reader that registration
     `configs/campaigns/v5_claim_25g83/registration_block5.md:4901-4902` provides for, and it must not also be a
     repair seat.
3. **Placement and D-174.** Rule on registration §14 Q4 (`registration_block5.md:5968-5969`) in a dated addendum
   covering:
   - which plan §9 rows print, at which Paper 1 or CP-X sites, and beside which fixed sentences;
   - supersession of the 2026-09-05 "D-174 SELECT FALLBACK" disposition (`docs/paper/results-fill-registry.md:3-15`).
     D-174 itself expires only "at submission or on Ed's written instruction" (`docs/decision_log.md:11360-11367`),
     so this needs Ed's written instruction or a dated D-174 addendum;
   - the Paper 1 title against D-165's protocol-first title rule (`results-fill-registry.md:309-317`).
4. **The paper-input route.** Choose one:
   - **(a)** Extend D-173 custody: add production roles for floors, the D-165 close-out and the disclosures, plus a
     CLI around `joulewise/paper_rendering.py`.
   - **(b)** Port #652 to DLE-1 inputs. It would read a frozen bundle bound by the dry-run record's digests, and a
     DLE entry would adopt that in place of plan §1 item 3's `open_paper_input` for Block-5 inputs.

   Either route must work in both D-189 branches: with the claim-evidence sidecar present, or absent (§2 A2).
   **Recommended: (b).** #652 already prints the whole contrast census with a row-for-row validator. D-173 has
   roles for only two of the families the plan prints.
5. **Print precision per family.** RS item 83 ruling 2 sends digits to a registry that has no active Block-5 rule
   (`RUN_STATE.md:343`; #652's own NEEDS-LEAD note). The candidate is `paper_rendering.py:46-49`: 3 decimals in J,
   6 in J/token, estimates rounded half-even, interval endpoints rounded outward. Re-point ruling 2 to whatever you
   adopt.
6. **Named independent hand-check sources.** These are needed for each of the seven uncovered families, for the
   exempt load-correlated line, and for the reason codes. DLE-0 says the coverage audit names the sources
   (`DEVIATION-LOG.md:63`), but it does not: it names L9's own producing code and says a source check is still
   needed (`docs/analysis/b5/LEAN-COVERAGE-AUDIT.md:70-82`, `:105`). Also name the hand-check reader(s).
7. **The analysis-program addendum (registration §11 item 4, `registration_block5.md:5519-5521`).** Either write it
   before the event, or record a DLE entry saying that the r4 tag, the record's `analysis_commit` and the verdict's
   `release_checkout.commit` satisfy it.
   - **Recommended: write it.** It covers the r4 tree plus the release-check commit's `release_b5.py`, recompute,
     comparator and bars. The command is in §5 A6.
8. **The post-event information rule.** Decide:
   - who the named readers are;
   - who the named blind repair seats are;
   - that released values, including the filled paper, stay out of git until the gate and any repairs close. The
     repository is public and agents start by reading `RUN_STATE.md`;
   - that PR bodies and repair briefs carry structure only;
   - that a reader log is kept outside the repository.
9. **Paper wording.** Decide:
   - whether registered fixed sentences print verbatim or paraphrased (Paper 1 `DRAFT_NOTES.md` question 5);
   - a gloss table from every registered refusal or outcome code to its sentence;
   - whether the composite sentences (abstract, conclusion, recompute summary) are pre-written as a finite grid of
     variants. This is recommended, not required: the Paper 1 plan allows results paragraphs to be written after
     release (`docs/strategy/2026-10-27-paper1-contingency.md:89-91`).
10. **Disclosures and Block-6 hardening.**
    - **(i)** Paper 1 must disclose that GAMMA floor-resolution status and reason words were read before release,
      under a structural ruling, and that D5b's relabel was ruled after that read (`DEVIATION-LOG.md:228-236`,
      `:252-274`).
    - **(ii)** Decide whether Block 5's paper discloses the per-family count channel (§2 C4), and whether the Block-6
      public verdict drops counts on `agree`.
11. **Which Paper 1 is canonical, and its blind provenance.** Choose between `lane/2026-10-27-paper1-draft` and the
    #531 outline. Open its PR, tag the commit written before unseal, and point `CANONICAL.md`'s Paper rows at it.
    Today they point to the frozen `docs/paper/draft-v1.md` (`CANONICAL.md:75`).

Process defaults I set without asking, per the standing rule on sensible process calls:
- Ed's unseal OK is cited in the release event by Gmail message id and time.
- The paper tier (contingency plan §2) is recorded by date before anything is read.
- The release runs from a fresh worktree.

---

## 1. Where the two seats agreed (stated once)

- The release event has no template, no command and no stated order relative to reading; the section is empty
  (`SEAL_RECORD.md:624-628`).
- No Block-5 Results renderer is on `main`.
  - Plan step 11's `render_results_fills.py` is the retired Window-A template and stops before printing
    (`scripts/render_results_fills.py:975-989`).
  - The dry run records `results_rendering_not_run_no_block5_template` (`joulewise/b5_analysis/dry_run.py:1759`).
- The Q-RENDERER obligation depends on the gate that DLE-0 abolished.
- Placement is unruled (plan line 697: "no row below has a placement").
- The hand check of uncovered leaves (RS item 83 ruling 3, `RUN_STATE.md:344`) has no worklist and no record form.
- The disclosure producer writes `<sha>.released.txt`, the values, beside `<sha>.unreleased.txt`
  (`scripts/produce_b5_disclosures.py:213-216`).
- The runbook lets a blind seat trace a hold "from `$OUT/comparison.json`" without naming the structure-only tool
  (`docs/analysis/b5/RELEASE-RUNBOOK-lean.md:71`, `:100`).
- The verdict carries no digest of the dry-run record or of `recompute.json`/`comparison.json`, so the release event
  has to hash them.
- Three programs print a science result to the terminal (`registration_block5.md:4906-4911`).

---

## 2. Findings

Severity: **HIGH** means it blocks an orderly, licensed unseal or would publish a false statement. **MEDIUM** means
fragile, manual or a blinding risk. **LOW** means hygiene.

### A. Missing, manual or fragile steps

**A1 (HIGH). The release event is an unscripted prose edit, and its boundary is misstated.**

What the registration requires:
- After the dry run completes, "the lead records a release event tying the sealed SHA-256s of this file, the
  analysis plan and the catalog to the final harvest records", as a section appended to the seal record
  (`registration_block5.md:4842-4848`).
- After the event, the readers are "the lead, and the results cold gate" (`:4901-4902`).

What exists:
- The section reads "Nothing is recorded here yet" (`SEAL_RECORD.md:626`).
- `CANONICAL.md:47` defers to "the plan's release section and `RUN_STATE.md`".
- The runbook ends at "Ask Ed for the unseal OK" (`RELEASE-RUNBOOK-lean.md:70`), and says the restricted outputs
  are not opened "before the unseal OK" (`:100`). The registration makes the recorded event the boundary, not the
  OK.

Fix: §5 C, a template plus hashing commands. The event is committed and merged before any restricted file is opened.

**A2 (HIGH). Paper numbers are not mechanically bound today.**
- On `main`, the only mechanical seam is D-173 custody plus `joulewise/paper_rendering.py` (`render_reported_energy`,
  `render_claim`, `render_d165`; fixed precision at `:46-49`).
  - Nothing outside tests calls these renderers. I searched `joulewise/`, `scripts/`, `tools/` and `docs/`; the only
    hits are the unrelated `render_claim_verdicts`.
  - The supply map has three roles and no pending roles: `production.claim_evidence.gamma.v5` and two
    `production.reported_energy_parents.*.v5` (`configs/paper_supply/supply_map.json`).
  - There is no role for floors, the close-out or the disclosures.
- The only Block-5 renderer, #652 (`lane/2026-11-05-b5-results-renderer` at `15dd5c8f7`), is unmerged. It requires
  `B5-RELEASE-RECORD.json` with `mode == 'release'` (`joulewise/b5_analysis/results_renderer.py:183-186`, `:265` at
  `15dd5c8f7`). It therefore refuses DLE-1 custody, which has only the blind dry-run record. It copies JSON numbers
  losslessly and leaves precision as NEEDS-LEAD.
- **Reconciled.** Seat 1 says the claim-evidence role is exercised blind at step 9b. Seat 2 says that role "needs a
  step-9b sidecar that D-189 says will not exist". Both are partly right:
  - `_claim_open` opens claim-evidence custody only when `claim_side_bound_not_issuable` is false
    (`dry_run.py:1555-1575`).
  - D-189 item 4 says a fill that needs the claim-side bound "refuses cleanly downstream" when no sidecar exists
    (`docs/decision_log.md:12251-12262`).
  - Which branch Block 5 is in is a blinded outcome class. The route chosen in Decision 4 must therefore render both
    branches. The governed receipt for prose with no verdict (A145 `CLAIM-NONISSUANCE-RECEIPT-01`) is SHELVED
    (`TASK_QUEUE.md:1254`), so the absent branch needs its own rule.

**A3 (HIGH). The renderer obligation points at a gate that no longer exists.**
- Q-RENDERER (`SEAL_RECORD.md:631-638`): a renderer written after release prints every row of the fill input's
  contrast census with its issued status, selects none, has a row-for-row validator, and "passes the Results cold
  gate before any number it prints is used".
- DLE-0 (`DEVIATION-LOG.md:38-64`) replaced step 12 with recompute agreement. That agreement checks step-11 JSON,
  not rendered Markdown.
- The same removal leaves the registration's post-event reader set (`registration_block5.md:4901-4902`) with only
  the lead.

This is Decision 2.

**A4 (HIGH). The release condition cannot pass a registered null state.**
- `Comparison.numeric` gives DISAGREE `missing_or_null` unless both values are finite. So both sides null is also
  DISAGREE (`scripts/compare_b5_recompute.py:211-222`).
- `compare_contrasts` compares `dbar_j`, `s_d_j`, `se_j`, the intervals, `D_j` and the floor parts
  unconditionally (`:2224-2253`).
- `compare_arms` compares `floor_abs_j`, `floor_cmp_j` and `floor_gate_j` for every resolution whatever its status
  (`:2150-2154`).
- A refused resolution must carry null values (D-190 body, `decision_log.md:12270`). A not-estimable contrast has
  no estimate, interval or D (D-190).
- The comparator does handle the words: `threshold_free` drops the threshold tests for `not_estimable`
  (`:2269`). But the numeric rows still fail.
- #652's notes flag the same gap ("some legitimate D-190 releases cannot yet pass this upstream gate").
- DLE-3 makes the D5 case a hold by design (`DEVIATION-LOG.md:325-347`). Nothing covers a *registered* null, which
  plan §3.1 says "is the result and is printed as such" (`analysis_plan_block5.md:178`).

This is Decision 1. Nothing here says whether r4 is in such a state.

**A5 (MEDIUM). Placement is unruled, and the methods paper's selector forbids results.**
- Registration §14 Q4 is open (`registration_block5.md:5968-5969`). Plan §9 says "no row below has a placement"
  (`analysis_plan_block5.md:697`), and plan step 11 renders only "results fills for adopted placements" (`:171`).
- **Wording corrected.** Seat 1 wrote "D-174 still forbids printing any _v5 result". More precisely:
  - D-174 is a scope freeze (`decision_log.md:11360-11367`).
  - The 2026-09-05 "D-174 SELECT FALLBACK" disposition is what places no `_v5` result and permits only
    `METHODS_DIAGNOSTIC` (`results-fill-registry.md:3-15`; `docs/paper/fill-rehearsal/branch-selection.md`).
  - The placement proposal is "COMPLETE ... and NON-FILLABLE pending adoption" (`results-fill-registry.md:55-59`).
- No decision supersedes the fallback.
- A ruling made after unseal would be informed by the outcome.

**A6 (MEDIUM). The analysis-program addendum is missing.**
- Registration §11 item 4 pins the L9 code "before the release event" by an addendum that names the files, their
  SHA-256s and the desk commit, written by a blind seat (`registration_block5.md:5519-5521`). Plan §11 repeats it
  (`analysis_plan_block5.md:736-765`).
- The seal record has addenda 1-5, for the harvest, the errata and the meter, and none for the analysis code.
- DLE-3 calls the rebind "the tag and the re-run" (`DEVIATION-LOG.md:232-233`) but does not say this replaces
  §11 item 4.
- Under DLE-1, three further programs decide the release, from a later checkout: `release_b5.py`, the recompute
  and the comparator, plus the bars. That commit is recorded only in `$OUT/verdict.json`.

This is Decision 7.

**A7 (MEDIUM). The hand check has no independent source, no worklist and no record form.**
- **Reconciled.** Seat 1 says the coverage audit names the sources; seat 2 says it does not. Seat 2 is right in
  substance:
  - Audit §2 (`LEAN-COVERAGE-AUDIT.md:70-82`) names L9's own producing code (for example `_monitor_lines`,
    `disclosures.py:870-933`) and the plan lines.
  - It then says: "For a quantity absent from lean output, that hand check needs another derivation/source check; it
    cannot compare two nonexistent values" (`:105`).
  - Checking L9's output against L9's code is circular.
  - DLE-0's "which that audit names" (`DEVIATION-LOG.md:63`) and DLE-1's "against the source the audit names"
    (`:124-125`) therefore point at nothing.
- Also uncovered: the exempt load-correlated line (`LOAD_LINE`), and reason-code evaluation (audit §2 item 7).
- "624" is historical (`LEAN-COVERAGE-AUDIT.md:105`). Count the real list after the event.

This is Decision 6. The worklist method is in C9 and §5 A5.

**A8 (MEDIUM). The runbook's `PINNED` is circular, and nothing ties it to the tag.**
- The runbook says `PINNED` "is the record's `analysis_commit`" (`RELEASE-RUNBOOK-lean.md:38`).
- `release_b5.py:275-276` then checks `record["analysis_commit"] == pinned`, so the check proves only
  self-consistency. The program does not check tag identity or ancestry; it only reads `seal_pins.json` at that
  commit (`:277-284`).
- DLE-3 makes the tag the authority (`DEVIATION-LOG.md:232-233`).
- Use `git rev-parse 'b5/analysis-r4^{commit}'`. Note that `b5/analysis-r3` resolves to the annotated tag object
  `654b9c8b3`; its commit is `68e47e1f2`. Seat 1 quoted the tag-object id.

**A9 (LOW to MEDIUM). Smaller fragilities, each checked.**
- **(a)** The runbook says stdout and `$OUT/verdict.json` are "the same bytes" (`RELEASE-RUNBOOK-lean.md:66`). They
  are not:
  - `finish()` writes compact JSON (`release_b5.py:452-459`);
  - `main()` prints with `indent=1` (`:494`).

  Cite the file's digest, not stdout's. Seat 2 also observed this on a fake-custody run. I verified it from the code.
- **(b)** Registration §12 rule 1 (`registration_block5.md:5693-5700`) is only partly automated:
  - The catalog digest from `harvest.json` is checked by L9 (`joulewise/b5_analysis/archive.py:262-263`, second-seal
    documents).
  - The registration digest (in `derived/harvest-thresholds.json`) and the inventory digest (in
    `derived/code-identity.json`) are checked by no program. `release_b5.py` checks 5 of the 8 `sealed` keys
    (`:73-75`); `seal_pins.json` has 8.
  - **Correction to seat 2's C2.** `derived/window_flags.json` is **restricted** until the event
    (`registration_block5.md:4883`, custody map). Do not open it by hand before the event; the catalog side is
    already covered by `archive.py`.
- **(c)** `release_b5.py` refuses any untracked file (`:163-168`), so run it from a fresh worktree.
- **(d)** The window index carries absolute archive and runs roots (`configs/analysis/b5/analysed_windows.json:12-15`).
  Moving or offloading an archive before the release breaks stage (a). Seat 1 cited a retention rule at
  `RUN_STATE.md:47`; that citation does not hold (see Dropped).
- **(e)** `--harvest-meter` is attached only when `withheld/meter.json` exists, and absence is silent
  (`release_b5.py:333-337`).
- **(f)** The runbook still names dry-j/dry-k and the lane branch (`RELEASE-RUNBOOK-lean.md:37`, `:45`).
- **(g)** `docs/process_traces/2026-11-07-b5-release-trace/extract_blind.py` has no test, and the runbook does not
  mention it. A search of `tests/`, `scripts/` and `docs/analysis/` finds nothing.
- **(h)** No first-reader log exists. #652's `reader`/`first_read_utc` fields are unmerged.
- **(i)** `docs/contracts/paper_comparison_rendering.md`, which #652 cites, was removed by the prune `71dea4e09`.

**A10 (MEDIUM). Work deferred to after the release conflicts with the blind-repair rule.**
- The repo trim is "the FIRST job after the block-5 release" (`RUN_STATE.md:1032-1034`, kernel task
  `FREEZE-BY-COMMIT-01`).
- Item 165's deferrals (`RUN_STATE.md:1043`) are also queued for after the release.
- After the event, only blind seats may write or review analysis repairs (`analysis_plan_block5.md:196-199`).
- The trim must wait until the release bundle is frozen and the renderer and filler are tagged. #652 imports
  comparator internals.

### B. Rendering that is not mechanically bound to the released record

**B1 (HIGH). No Paper 1 placeholder is filled by a program.**
- The fill index has 236 occurrences of 219 ids, 174 of them new (`docs/paper/paper1/fill_index.md:5-6` at
  `a1a5029fb`).
- Sources are assigned by id prefix: every `P1-B5-*` id gets one generic source (`build_fill_index.py` `source()`,
  `:20-42`).
- There is no filler and no fill map from id to (artifact, JSON pointer, transform, precision).
- `docs/paper/build/check_markdown.py` detects only `[...PENDING...]` (`:26`). It has no `FILL` pattern.
- `CANONICAL.md:75` still names `docs/paper/draft-v1.md`, which the registry calls frozen
  (`results-fill-registry.md:29-31`).

**B2 (MEDIUM). Branch selection is manual.**
- Sections 5.1.a-9.D of Paper 1 need a branch chosen from issued fields: `claim_evaluation.outcome`, `direction`,
  `claim_level_ceiling`, the leave-one-out flags, and the close-out `branch`/`dominance_sentence_licensed`/
  `subtitle_licensed`.
- The only selector on main accepts `METHODS_DIAGNOSTIC` alone (`branch-selection.md`).

**B3 (MEDIUM). Composite sentences would be written after release.** These are the abstract `P1-ABS-PART1`, the
`CP-X08-*` conclusions, `P1-RECOMPUTE-SUMMARY` and the 5.5.4 reason text.
- The Paper 1 plan allows this (`paper1-contingency.md:89-91`), so it is not a violation.
- But it is the one place where discretion meets the numbers. Decision 9 recommends a pre-written grid, with the
  licence lint as the backstop.

**B4 (MEDIUM). Reason text is free-form.**
- `P1-B5-CTR-NR-REASON` offers "no floor could be issued" as a reason for *not resolvable* (paper1.md:806).
- After D5b a floor-binding refusal is `floor_artifact_invalid`, which is `not_estimable` (`DEVIATION-LOG.md:252-265`).
- Render the reason from the issued code through a gloss table fixed blind.

**B5 (MEDIUM). The recompute paragraph has no producer and cites the wrong bars.**
- `P1-RECOMPUTE` and `P1-RECOMPUTE-SUMMARY` cite "tolerance from docs/registrations/block6_replication_DRAFT.md
  §12.3" (`fill_index.md:32`, `:179` at `a1a5029fb`). That is Block 6's tolerance.
- Block 5's bars are 1e-6 relative and 1e-6 absolute for joules and ratios, 1e-6 absolute for p, and exact for
  counts (`configs/analysis/b5/recompute_bars.json`, sha256 `2f65bba2…` = `RELEASE_BARS_SHA256`, `release_b5.py:58`).
  They were bound by RS item 83 ruling 1 (`RUN_STATE.md:342`).
- No per-family summarizer of `comparison.json` exists.

**B6 (MEDIUM). Nothing re-checks the files read after verification.** Stage (a) verifies digests once. Later reads
are not re-bound to them. Freeze a read-only bundle with `SHA256SUMS`, and have every renderer and filler verify it
(§5 D).

**B7 (MEDIUM). No licence lint covers the registration's own constraints.**
- `scripts/claims_lint.py` has a claims-ladder forbidden-language check (`:868-900`). It gives warnings only.
- No check covers the Block-5-specific rules listed in D below (rungs, both contrasts printed, dominance branch,
  fixed sentences, D-177 note, boundary label, sensitivity line, seven families only after the hand check).

### C. Where a person could unblind early, or stop being blind

**C1 (MEDIUM). `<sha>.released.txt` holds the values.**
- `write_disclosures` writes `<sha>.json`, `<sha>.unreleased.txt` (restricted items print "withheld until the release
  event", `disclosures.py:1351-1353`) and `<sha>.released.txt` (full values and RESTRICTED codes)
  (`produce_b5_disclosures.py:213-216`). The record names them `disclosure_released`/`disclosure_unreleased`
  (`dry_run.py:1751`).
- **Adjusted from seat 1.** Seat 1 proposed naming `*.unreleased.txt` as "the only view a blind seat may read". I do
  not adopt that.
  - Both files live under `dry-run/restricted/`, which until the event is read by automation only
    (`registration_block5.md:4895-4900`, `analysis_plan_block5.md:186-191`).
  - No step of the checklist needs either file before the event.
- Rule: no person opens anything under `dry-run/restricted/` before the event. After it, `released.txt` is the
  reference text for every §8 line.
- Rename it (for example `post-event.txt`) for Block 6.

**C2 (MEDIUM). Holds are traced "from `$OUT/comparison.json`" without naming the tool** (`RELEASE-RUNBOOK-lean.md:71`).
- That file holds values, differences and bars (`:96`).
- The r3 trace did it correctly, through `extract_blind.py` under `python3 -I`
  (`docs/run_reports/2026-11-07-b5-release-hold-trace.md:3-9`).
- Name the tool in the runbook, add a test, and move it to `scripts/`.

**C3 (HIGH). Order of operations.** The registration makes the recorded event the precondition for reading
(A1). Nothing orders "commit the event, then open". §5 C fixes that order.

**C4 (MEDIUM). The public verdict's counts carry an energy-derived cardinality.**
- `release_b5.py` copies each family's `pass`/`fail` counts and the step-11 coverage counts into the public verdict
  (`:375-397`).
- In `compare_disclosures`, `loo_magnitude` rows exist for each quad that either side selects as raising the
  leave-one-out magnitude trigger, "a movement beyond a quarter of the floor"
  (`compare_b5_recompute.py:3243-3260`). So the `contrast_j` and `outcome_word` pass counts grow with that number.
- That number is a "pass/fail derived from a science energy", which registration §8 item 2 restricts
  (`registration_block5.md:4828-4831`).
- I did not compute or look for that number in any published count. This is Decision 10(ii).

**C5 (HIGH). The repository is public, so released numbers must stay out of git.**
- `gh repo view` reports `PUBLIC`.
- Fresh agent seats start by reading `RUN_STATE.md`.
- So one released number committed to any branch, run report or PR body unblinds every later "blind repair seat"
  (`analysis_plan_block5.md:196-199`). The registration already warns about PR bodies
  (`registration_block5.md:4906-4908`).

This is Decision 8.

**C6 (MEDIUM). Delegating widens the reader set.** After the event the readers are "the lead, and the results cold
gate" (`registration_block5.md:4901-4902`). Handing hand checks or rendering to Sol or Opus sub-seats widens that
set. The release event should name every reader.

**C7 (LOW). Programs that print to the terminal.** These print a result on an ordinary run: `analyze-claims`, the
close-out without `--output`, `render_results_fills.py` (`registration_block5.md:4908-4911`), and after the event the
`paper_rendering.render_*` functions. Run them only after the event, and only into custody or the paper working
copy, never into a shared terminal log.

**C8 (LOW). `$OUT` location.** `$OUT` is created 0700 (`release_b5.py:463-473`). Put it under the same unsynced
restricted parent as the custody root, never in a synced folder (iCloud, Dropbox).

**C9 (MEDIUM; found in synthesis). A worklist extracted before the event from the real `comparison.json` can carry
outcome-class information.**
- Seat 1's step 3 prints the real `coverage.uncovered_numeric`/`nonfinite`/`unmapped`/`absent_sources` leaf ids
  before the event.
- Membership of those lists depends on values. `uncovered-null-by-name:` admits a leaf only when its value is null
  (`compare_b5_recompute.py:3921-3930`, `:3953-3968`). Leaves such as the leave-one-out magnitude rows exist only
  for some outcomes.
- Build the worklist instead from the synthetic full-size run's `comparison.json` (§5 A5), by leaf pattern. Then
  intersect it with the real list after the event.

### D. What Paper 1 says that the registration or record does not license

All lines are `paper1.md` at `a1a5029fb`. Each item was checked against the source in the third column.

| # | Paper text | Problem (evidence) | Fix |
|---|---|---|---|
| P1 (HIGH) | 655-656: "The registered agreement tolerance is ... within 1 mJ and every printed quantity ... within half a unit of its last printed digit" (also 895) | That is Block 6's S-13 set. Block 5's bars are `recompute_bars.json` (1e-6 relative/absolute; counts exact), bound by a lead ruling (RS item 83 ruling 1, `RUN_STATE.md:342`) and adopted in DLE-0, not by the registration | Print the Block-5 bars per family: "fixed blind before release (DLE-0)" |
| P2 (HIGH) | 643: "A release event then tied the digests ...; the registered analysis ran after it" | Under DLE-1 the printed numbers are the blind dry run's L9 outputs, made *before* the event and verified byte for byte (`DEVIATION-LOG.md:96-110`). Registration `:4842-4844` said otherwise; DLE-1 is the deviation | State the DLE-1 order; list it in `P1-DEV-LIST` |
| P3 (MEDIUM) | 655-656 and 1255: "every printed quantity" / "Every headline number" recomputed; 38, 91 "from the raw records" | Seven families are not recomputed, and the load line is exempt (`LEAN-COVERAGE-AUDIT.md` §2-§3). The recompute takes recorded judgments as inputs: selection, anchors, calibration fits, exclusions, NEG-8 membership (`:107-118`). "Headline" is defensible for the core arithmetic; "every printed quantity" is not | "core numbers ... from the raw power records, with the recorded collection-time judgments as inputs"; list the hand-checked families |
| P4 (HIGH) | 1222: "A second laptop held the restricted data for analysis under an account no agent used" | Agents ran dry runs with custody under the same account (`RUN_STATE.md` item 108, line 465 at `16c37a4bf`), and the lead ran probes on dry-j custody (`b5-release-hold-trace.md:18`). Custody "is kept by rule, not by the file system" (`registration_block5.md:4853`) | Describe custody by rule and structure-only probes honestly |
| P5 (HIGH) | 1260-1262 and 1364: every outcome sentence "is fixed in the registrations" / "fixed ... before the data existed" | The branch prose was written 2026-10-27 (`e99bdff52`..`037582d69`). Collection closed 2026-10-12 (`RUN_STATE.md:16`). Only the plan's fixed sentences are registered | "written before release, at commit ...", and tag that commit (Decision 11) |
| P6 (MEDIUM) | 621 and 1240: "a session refuses to start if any file it reads differs from the sealed bytes" | A code difference is `code.executed_differs_from_sealed`, found at harvest, and it removes the window (`registration_block5.md:1546-1547`, `:3948`). The one identity refusal at the arm is OS build plus machine model (§4.7, `:2602`) | Correct the mechanism |
| P7 (MEDIUM) | 629 with `P1-DEV-LIST` sources "seal record, replication §17, BYTES addenda" (`fill_index.md:30`) | The list omits `docs/analysis/b5/DEVIATION-LOG.md` (DLE-0..3: release procedure, D1 printed key, D5b outcome-label mapping) and D-188..D-190 | Add them; describe D5b as a blind, post-collection change to the reason mapping |
| P8 (MEDIUM) | 634-635: no person or agent read "... outcome word" | True for words. The pre-release structural read of status and reason words (Decision 10(i)) must be disclosed beside it | Add the disclosure |
| P9 (MEDIUM) | 717-718: `P1-B5-B-SHARE`, B ÷ (h + B) | Not a registered quantity. "Every printed number is MEASURED or DERIVE" (`analysis_plan_block5.md:713`), and unregistered analyses are exploratory (`:771-772`) | Drop it, or label it exploratory |
| P10 (LOW) | Title (19): "... Attribution Limits ..." | The protocol-first title fixed before collection is "JouleWise: Timing Sensitivity of Phase-Energy Assignments on Apple Silicon". "Attribution-limited" appears only as the branch-A subtitle (`results-fill-registry.md:309-317`) | Rule blind (Decision 3) |
| P11 (MEDIUM) | 806 and §9.C (1377-1378): "not resolvable ... a finding about resolution" | Must not be applied to `not_estimable`. Under D-178/D-189, non-issuance "is not an empirical negative result" (`decision_log.md:12253`) | A gloss table with a branch per code |
| P12 (LOW) | `docs/paper/draft-v2-skeleton.md:874-882`: no release or archive locator has issued | Once Block-5 numbers print, the evidence section must name the custody, the dry-run record digest, the bundle `SHA256SUMS` and the release event | Update with the event |

**Licence constraints, for the lint (seat 1's list, each verified):**
1. ALPHA and BETA are L1 only. ALPHA beside BETA is side by side, "labelled as collected in separate windows in a fixed order"
   (`registration_block5.md:1637`), and is never a comparison (`analysis_plan_block5.md:768`).
2. GAMMA contrasts are L2 only if the claim gate allows it (`registration_block5.md:1638`).
3. The claims ladder's forbidden words apply (`docs/contracts/claims_ladder.md` ladder table).
4. Both contrasts print whatever their status, and none is selected (Q-RENDERER). A refused or unresolved contrast is
   not equality or zero effect.
5. The dominance sentence and the subtitle print only on branch A (`analysis_plan_block5.md:357-358`). Every ratio
   prints with numerator, denominator, n and "point diagnostic; no interval" (`:359-360`). R_cm passing licenses no
   physical-common-time claim (`:354-355`).
6. The fixed sentences print verbatim or under the Decision 9 rule (`disclosures.py:36-55`): attribution floor, gross
   energy, cross-window agree/differ, decision-vs-floor, leave-one-out, machine boundary.
7. The D-177 limitation goes beside every phase-energy sentence (`registration_block5.md:1641-1642`).
8. Boundary label: `M3 Max / MLX / powermetrics SoC rails`. The meter is a cross-check, never a claim (`:1643-1650`).
9. The sensitivity line never prints as the result (`analysis_plan_block5.md:771`).
10. The seven uncovered families print only after the hand check.

---

## 3. Registered quantity, issuing artifact and binding

Condensed from seat 2's table. "Bound today" is the state on `main`.

| Plan quantity | Issuing artifact | Bound today | Independent check | Needed |
|---|---|---|---|---|
| Reported cells: mean, interval, J/token, n_r, n_b (§4) | step-10 `outputs/projection-<pack>.json`; D-173 role exists | renderer exists, no caller | compared | fill map, precision |
| Attribution floor, attaining member (§4.7) | projection `binding.attribution_floor_j` | manual | value compared; `attained_by` uncovered | map; hand-check member id |
| Floors abs/cmp/operative, n (§5) | aggregate floor artifact, extraction reports | manual; no D-173 role | compared | map; operative = max check |
| R, R_cm, branch, subtitle (§6) | `closeout.json` | manual; no production role | compared incl. `dominance_branch` | bind branch and subtitle to close-out flags |
| Contrasts: d̄, intervals, floor gate, Holm p, outcome, ceiling (§7) | `claim-verdicts.json`, `results-fill-input.json` | #652 candidate (refuses DLE-1) | compared; null states fail (A4) | Decisions 1 and 4; branch selector; gloss |
| §7.3 ratio, per-token difference | disclosure record | manual | compared (log internals exempt) | map |
| Load-correlated line (§8.1) | sensitivity, disclosure | manual | **not compared** (`LOAD_LINE`) | hand check |
| Attempt history, G10; hazards; monitor; battery; temperature; NEG-8 census; selection (§8.1) | disclosure lines | manual | **not recomputed** | named sources (Decision 6) |
| Whole machine (§8.2) | disclosure, `withheld/meter.json` | manual | numbers compared; k/n text not | hand check k/n; confirm meters offered (A9e) |
| Recompute agreement | `comparison.json` | none; wrong bars cited | n/a | summarizer with Block-5 bars |
| Release event, deviations | seal record, DEVIATION-LOG, D-188..190 | none | n/a | write event; fix sources |

---

## 4. Reconciliation log, and what was dropped

**Where the seats disagreed, and what I decided after checking:**

1. **Claim-evidence role.** Each seat is partly right. The role is exercised only in the issuable branch
   (`dry_run.py:1555-1575`; D-189 item 4). See A2.
2. **Hand-check sources.** Seat 2 is right in substance. The audit names producing code, not an independent source
   (`LEAN-COVERAGE-AUDIT.md:105`). See A7.
3. **Renderer.** Both are right. None is on `main`. #652 exists, unmerged, and refuses DLE-1 custody. See A2.
4. **`*.unreleased.txt` as the blind view (seat 1).** Not adopted: it is a restricted path, and no step needs it.
   See C1.
5. **Extracting the worklist before the event from the real `comparison.json` (seat 1, step 3).** Replaced by a
   worklist built from the synthetic run. See C9.
6. **Seat 2's C2, "derived/window_flags.json ... releasable".** Wrong: it is restricted
   (`registration_block5.md:4883`). The catalog digest is already checked by `archive.py:262-263`. See A9b.
7. **D-174 wording (seat 1).** Corrected: the fallback disposition places no result; D-174 is a scope freeze. See A5.
8. **The r3 tag id (seat 1).** `654b9c8b3` is the annotated tag object; the commit is `68e47e1f2`. See A8.
9. **Writing composite sentences after release (seat 2).** A recommendation, not a violation, because the
   contingency plan allows it. See B3.
10. **Seat 2's P3.** Narrowed to "every printed quantity" and "from the raw records". "Headline numbers" is defensible.

**Dropped or not relied on (unverified or wrong):**
- Seat 1's `RUN_STATE.md:47` "retention" citation. Line 47 is the pre-arm bracket step at both `16c37a4bf` and
  `bd7a3efcd`, and no such rule was found by search. The underlying risk is kept, on the evidence of the absolute
  index paths.
- The second half of seat 2's P4 ("Cloud machines ... never held real or blinded data"). Not checked; not relied on.
- The specific hand-check sources in seat 2's §3 table (`hazards/arm.json`, monitor journals, `derived/` files).
  Kept as candidates for Decision 6, not as verified sufficient sources.
- Seat 2's effort estimates (2-4 h of rulings, about 1 day of code). Reported as the seat's estimate only.
- Seat 2's reference to `tests/independent_recompute/test_input_gate.py:522-531` (via #652's notes). Not opened.
- The `verdict.json` file mode (0644). Not re-run; minor.
- Seat 1's step-0 `os.path.isfile(... withheld/meter.json)` probe. It stats a restricted path. Take meter presence
  from the releasable `harvest.json` output list instead (§5 B1).

---

## 5. Ordered checklist with commands

**Conventions.**
- `WT` is a fresh worktree under `/Users/edr/code/CapstoneProject/jw-wt/`.
- `CUSTODY` is the r4 dry-run custody root, the folder that holds `dry-run/B5-BLIND-DRY-RUN-RECORD.json`.
- `PARENT=$(dirname "$CUSTODY")` must be restricted and unsynced.
- Run everything as `nice -n 19 taskpolicy -b python3.13 -B` with `TMPDIR=/private/tmp/jwburn-release`.
- Items marked **(build)** do not exist yet.
- **No step before C5 opens any restricted file.**

### A. Before the event, while the lead is blind (in parallel with the r4 dry run)

- **A1. Rulings.** Make Decisions 1-11 as DEVIATION-LOG entries DLE-4 onward, plus a dated D-174/§14 Q4 addendum.
  Each carries the DLE signing statement (`DEVIATION-LOG.md:30-31`).
- **A2. Paper tier.** Record the tier by date and completion in RUN_STATE (contingency plan §2).
- **A3. Paper 1.**
  - Apply P1-P12.
  - Fix the `fill_index` sources: Block-5 bars, and DEVIATION-LOG plus D-188..190 in `P1-DEV-LIST`.
  - Open a PR for it, point `CANONICAL.md` at it, and tag the outcome text written before unseal:

  ```bash
  git tag -a paper1/pre-unseal-$(date -u +%Y%m%d) <paper1 commit> -m "Paper 1 outcome text written before the block-5 release event"
  git push origin paper1/pre-unseal-$(date -u +%Y%m%d)
  ```
- **A4. (build)** Merge each of these with synthetic tests:
  - the Decision-4 renderer: #652 ported to `--bundle`, refusing unless the seal record's "Release event" names the
    record's and the verdict's SHA-256, and rendering both D-189 branches;
  - `docs/paper/paper1/fill_map.json`, mapping id → (bundle role, RFC 6901 pointer, transform, precision);
  - `fill_paper1.py`, which selects branches from issued fields and refuses any unmapped id;
  - a `{{FILL:` pattern in `check_markdown.py`;
  - the licence lint (§2 D);
  - the per-family `comparison.json` summarizer with the Block-5 bars;
  - the Decision-1 comparator change, if adopted.
- **A5. Synthetic dress rehearsal and blind worklist.**

  ```bash
  mkdir -p /private/tmp/jwburn-release/tmp
  TMPDIR=/private/tmp/jwburn-release/tmp nice -n 19 taskpolicy -b python3.13 -B scripts/b5_e2e_synthetic.py \
    --scratch /private/tmp/jwburn-release/run --out /private/tmp/jwburn-release/out --workers 7 --keep-custody
  # (build) a wrapper that runs release_b5.py on the synthetic custody (test_release_b5's builder is the model),
  # then steps C4-F below unchanged, on synthetic data. From the synthetic comparison.json, list the leaf
  # PATTERNS of coverage.uncovered_numeric / named exemptions that the adopted placement will print; that is the
  # hand-check worklist, with columns: leaf pattern, paper site, named source (Decision 6), reader, result.
  ```
- **A6. The analysis-program addendum** (Decision 7). After the r4 tag exists:

  ```bash
  R4=$(git rev-parse 'b5/analysis-r4^{commit}')
  git ls-tree -r --name-only "$R4" -- joulewise scripts configs/analysis/b5 pyproject.toml env/analysis-lock.txt |
    while read -r f; do printf '%s  %s\n' "$(git show "$R4:$f" | shasum -a 256 | cut -d' ' -f1)" "$f"; done \
    > /private/tmp/jwburn-release/b5-r4-program-files.sha256
  shasum -a 256 /private/tmp/jwburn-release/b5-r4-program-files.sha256
  ```

  Append "Addendum 6: the analysis program (L9) and the release-check programs" to `SEAL_RECORD.md`. Include: the
  commit, the tag, the list digest, and the release-check commit's `release_b5.py`/recompute/comparator/bars digests.
  It must be written by a blind seat.
- **A7. Information rule** (Decision 8). Name the readers and the blind repair seats. Released values stay outside
  git. The reader log is `$PARENT/READER-LOG.txt`.
- **A8. Optional hardening** (Block 6, or a cited rebind now):
  - add `record_sha256` and the `recompute.json`/`comparison.json` digests to the verdict;
  - drop per-family counts on `agree`;
  - move `extract_blind.py` to `scripts/` with a test;
  - fix runbook lines 37, 38, 45, 66, 71 and 100;
  - rename `released.txt`.

### B. Release check at r4 (structure only)

**B1. Bindings.**
```bash
cd /Users/edr/code/CapstoneProject/jw-wt/handoff && git fetch origin --tags
git worktree add --detach /Users/edr/code/CapstoneProject/jw-wt/b5-release origin/main
cd /Users/edr/code/CapstoneProject/jw-wt/b5-release
test -z "$(git status --porcelain --untracked-files=all)" || echo "checkout not clean"
PINNED=$(git rev-parse 'b5/analysis-r4^{commit}')           # from the tag, never copied from the record
git merge-base --is-ancestor "$PINNED" HEAD && echo "pinned commit is on this history"
REC="$CUSTODY/dry-run/B5-BLIND-DRY-RUN-RECORD.json"          # the structure-only record, outside restricted/
python3 -I - "$REC" "$PINNED" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
print("mode", r["mode"], "completed", r["completed_without_tooling_refusal"], "commit_matches_tag", r["analysis_commit"] == sys.argv[2])
print("windows", [(w["pack"], w["plan_id"]) for w in r["windows"]])
PY
INDEX=configs/analysis/b5/analysed_windows.json
want=$(python3 -I -c 'import json,sys;print(json.load(open(sys.argv[1]))["window_index_sha256"])' "$REC")
[ "$(shasum -a 256 "$INDEX" | cut -c1-64)" = "$want" ] || { git show "$PINNED:$INDEX" > "$PARENT/analysed_windows.json"; INDEX="$PARENT/analysed_windows.json"; }
```
Confirm that D5 is answered per DLE-3 (`DEVIATION-LOG.md:325-347`) before running B2. Take meter presence per
pack from each window's releasable `harvest.json` output list, not by stat'ing `withheld/`.

**B2. The check.**
```bash
OUT="$PARENT/release-check-$(date -u +%Y%m%dT%H%MZ)"
mkdir -p /private/tmp/jwburn-release && TMPDIR=/private/tmp/jwburn-release \
nice -n 19 taskpolicy -b python3.13 -B scripts/release_b5.py --custody "$CUSTODY" --window-index "$INDEX" \
  --pinned-commit "$PINNED" --restricted-out "$OUT" --workers 10 > "$PARENT/verdict-stdout.json"; echo "exit=$?"
RCHK=$(git rev-parse HEAD)
```
Exit 0 is required. On a hold, trace only with
`python3 -I docs/process_traces/2026-11-07-b5-release-trace/extract_blind.py "$OUT/comparison.json" "$OUT/blind-extract.json"`.
Never open `comparison.json`, `recompute.json` or anything under `dry-run/restricted/`.

### C. The release event: write and merge it, then read

**C1. Verify, structure only.**
```bash
python3 -I - "$OUT/verdict.json" "$PINNED" <<'PY'
import json, sys
v = json.load(open(sys.argv[1]))
assert v["verdict"] == "agree" and v["reason"] is None and v["pinned_commit"] == sys.argv[2]
assert all(f["verdict"] == "agree" for f in v["stages"]["comparator"]["families"].values())
print("release_checkout", v["release_checkout"]["commit"])
PY
```

**C2. Registration §12 rule 1, for the part no program checks.** For each analysed window, the registration digest
in `derived/harvest-thresholds.json` and the inventory digest in `derived/code-identity.json` must equal the seal
record. Both files are releasable. Do **not** hand-open `derived/window_flags.json`, which is restricted; its
catalog digest is checked by `archive.py:262-263`.

**C3. Ed's OK.** Record the Gmail message id and time.

**C4. Collect the digests.**
```bash
{ echo "record $(shasum -a 256 "$REC" | cut -d' ' -f1)"
  for f in verdict.json recompute.json comparison.json; do echo "$f $(shasum -a 256 "$OUT/$f" | cut -d' ' -f1)"; done
  echo "bars $(git show "$RCHK":configs/analysis/b5/recompute_bars.json | shasum -a 256 | cut -d' ' -f1)"
  echo "index $(shasum -a 256 "$INDEX" | cut -d' ' -f1)"
  git show "$PINNED":configs/analysis/b5/seal_pins.json | python3 -I -c 'import json,sys;[print("sealed",k,v) for k,v in sorted(json.load(sys.stdin)["sealed"].items())]'
  python3 -I -c 'import json,sys;r=json.load(open(sys.argv[1]));print("analysis",r["analysis_commit"],r["window_index_sha256"]);[print("window",w["pack"],w["plan_id"],w["harvest_record_sha256"]) for w in r["windows"]]' "$REC"
  echo "pinned $PINNED release_check $RCHK"
} > /private/tmp/jwburn-release/b5-release-event-digests.txt
```
Hashing restricted files reads their bytes into `shasum`, not into a person's view. This is the same automation
stage (a) performs.

**C5. Append "## Release event" to `SEAL_RECORD.md`.** It contains:
- the UTC time, the signer and Ed's OK id;
- every C4 line;
- the analysis tag;
- the release-check commit (and tag, if A8 tags it);
- Addendum 6, by reference;
- DLE-0..n and D-188..190, by reference;
- the named readers and the blind repair seats (Decision 8);
- the statement: "Before this entry the signer had seen no Block 5 energy or outcome value."

Commit it on a branch, open a PR, merge it (per the merge authorization), and confirm it is on `origin/main`.
**Only then may the named opener read.**

### D. Freeze the release bundle

```bash
BUNDLE="$PARENT/b5-release-bundle-r4"
python3 -I - "$CUSTODY" "$OUT" "$BUNDLE" <<'PY'
import hashlib, json, sys
from pathlib import Path
c, r, b = map(Path, sys.argv[1:]); rec = c / "dry-run/B5-BLIND-DRY-RUN-RECORD.json"; b.mkdir(mode=0o700); sums = set()
def put(src, name):
    d = src.read_bytes(); h = hashlib.sha256(d).hexdigest(); dst = b / name
    dst.parent.mkdir(parents=True, exist_ok=True, mode=0o700); dst.write_bytes(d); sums.add(f"{h}  {name}"); return h
put(rec, "B5-BLIND-DRY-RUN-RECORD.json")
for row in json.loads(rec.read_bytes())["steps"]:
    for o in row["outputs"]:
        assert put(c / "dry-run/restricted" / o["name"], "outputs/" + o["name"]) == o["sha256"], o["name"]
for n in ("verdict.json", "recompute.json", "comparison.json"):
    put(r / n, "release/" + n)
(b / "SHA256SUMS").write_text("\n".join(sorted(sums)) + "\n")
PY
chmod -R a-w "$BUNDLE"; (cd "$BUNDLE" && shasum -a 256 -c SHA256SUMS | tail -1); shasum -a 256 "$BUNDLE/SHA256SUMS"
```
Put the `SHA256SUMS` digest in a dated addendum to the release event.

### E. Render, hand-check, gate

- **E1.** Add a `READER-LOG.txt` entry: seat, UTC time, files opened.
- **E2. Render mechanically, never transcribe.** Use the route from Decision 4, at tagged commits.
  - **(build)** Route (b):

    ```bash
    python3.13 -B scripts/render_b5_results.py --bundle "$BUNDLE" --seal-record docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md --prepare-checks "$CHECKS"
    python3.13 -B scripts/render_b5_results.py --bundle "$BUNDLE" --checks "$CHECKS" --out "$RESULTS"
    python3.13 -B scripts/render_b5_results.py --bundle "$BUNDLE" --checks "$CHECKS" --validate-rendered "$RESULTS"
    ```
  - Cross-check with D-173 (the reported-energy roles always; the claim role only if the record's step-9b row is
    `ok`). Run from a clean checkout at `PINNED`, because the receipts bind validator sources:

    ```bash
    cd <clean checkout at $PINNED> && python3.13 -B - "$CUSTODY/dry-run/restricted" > "$PARENT/rendered-lines.txt" <<'PY'
    import sys
    from pathlib import Path
    from joulewise import paper_custody as c, paper_rendering as r
    root = Path(sys.argv[1])
    for m in ("qwen3-1p7b", "qwen3-8b"):
        print(r.render_reported_energy(c.open_paper_input(c.ReportedEnergyParentsRef(role=f"production.reported_energy_parents.{m}.v5", runs_root=root))))
    PY
    ```
  - Every §8 line must equal `released.txt`, or the difference must be cited.
- **E3. The hand check.** Fill the A5 worklist for every uncovered leaf the paper prints, against `recompute.json`
  (where the recompute computes it) or the Decision-6 source. Keep the table with the bundle, out of git until G.
- **E4. The gate seat** (Decision 2) re-runs `--validate-rendered`, samples leaves against `$BUNDLE`, runs the
  licence lint, and checks §2 D.

### F. Fill Paper 1 (outside git until the gate and any repairs close)

```bash
python3 -I docs/paper/paper1/fill_paper1.py --provenance "$RESULTS/provenance.json" --map docs/paper/paper1/fill_map.json \
  --draft docs/paper/paper1/paper1.md --out "$PARENT/paper1.filled.md"          # (build)
rg -n '\{\{FILL:' "$PARENT/paper1.filled.md"        # only adopted STOP_FILL ids may remain
python3 docs/paper/build/check_markdown.py "$PARENT/paper1.filled.md"
python3 docs/paper/build/build_paper.py "$PARENT/paper1.filled.md"
```

Fill the remaining ids from these sources:
- `P1-RELEASE` from the event;
- `P1-DEV-LIST` from DEVIATION-LOG, D-188..190 and the seal-record errata and addenda;
- `P1-RECOMPUTE(-SUMMARY)` from the **(build)** summarizer over `$BUNDLE/release/comparison.json`.

### G. After the gate and any repairs close

- Commit the filled paper and the hand-check table.
- Update `CLAIMS_STATUS.md` and `PROJECT_STATUS.md`. RUN_STATE gets pointers only until then.
- Update `CANONICAL.md`'s "Block-5 release (unblinding)" and "Paper" rows.
- Close or supersede #648, #651 and #655, and #652 after the port.
- Then run `FREEZE-BY-COMMIT-01`. Its rehearsal re-runs E2 from the tags.
- Any defect found after the unseal goes through plan §3.2 item 3:
  - blind authors and reviewers;
  - a synthetic fixture that reproduces it;
  - every other fixture byte-identical;
  - outputs labelled "produced after unblinding" otherwise.
- `git worktree remove` the release worktree.

---

## Appendix A. Seat 1 report (Fable 5.1), verbatim

~~~~markdown
TOP: ["F1 (HIGH): The registration-required 'Release event' section (SEAL_RECORD.md:624-628) is still 'Nothing is recorded here yet'; no template, no hashing command, and no rule that it is committed before any restricted file is opened. The unseal is an unscripted prose edit.","F2 (HIGH): No Block-5 Results renderer exists. render_results_fills.py renders only the retired 1.5B/7B template and STOP_FILLs when both floor windows pass (:975-989); the dry run flags results_rendering_not_run_no_block5_template (dry_run.py:1759). Paper numbers would be hand-copied from restricted JSON. The only mechanical binding (paper_custody + paper_rendering.render_claim/render_reported_energy) covers two of the families, has no production role for dominance, floors or the §7.3/§8 lines, and has no caller outside tests.","F3 (HIGH): The Q-RENDERER obligation (SEAL_RECORD.md:632-636) requires a post-release renderer to pass 'the Results cold gate', which DLE-0 (DEVIATION-LOG.md:46-52) replaced with recompute agreement; a renderer written after release therefore has no gate. Needs a deviation-log entry before anything prints.","F6 (MEDIUM): Placement is unruled: registration §14 Q4 is open, D-174 still forbids printing any _v5 result in the methods paper, and the comparison placements are PROPOSED_STOP_FILL. The adoption ruling can and should be made blind, before the unseal.","U1 (HIGH): The disclosure producer writes <sha>.released.txt (values and RESTRICTED codes) beside <sha>.unreleased.txt (the redacted view) under dry-run/restricted/disclosures (produce_b5_disclosures.py:213-216); the name invites a blind tracer to open the wrong one. Checklist must name *.unreleased.txt as the only blind view.","F5 (MEDIUM): The runbook tells the operator to take PINNED from the record's analysis_commit (RELEASE-RUNBOOK-lean.md:38), making release_b5.py's commit check (:275-276) vacuous; take it from `git rev-parse b5/analysis-r4^{commit}` and require ancestry of HEAD.","F4 (MEDIUM): RS 83 ruling 3's hand check of uncovered step-11 leaves has no blind worklist and no record form; extract coverage.uncovered_numeric/nonfinite/unmapped/absent_sources identifiers only (structure) before unseal and prepare the check table.","U2 (MEDIUM): The runbook lets a blind seat 'trace from $OUT/comparison.json', a file of values; it should name extract_blind.py under python3 -I as the only reader.","Licence lint missing: the eight mechanically checkable constraints in §4 (rung from claim_ready_for_l2_l3, both contrasts printed with status, dominance branch A only for the subtitle, fixed sentences verbatim, D-177 note, boundary label, sensitivity line never the result, seven families only after hand check) are not enforced by any existing linter on the Paper 1 text."]
OPEN: ["Which mechanical route carries the paper: extend D-173 custody with production roles for d165_closeout and the floors plus a CLI around paper_rendering.render_*, or write the Q-RENDERER-style Block-5 Results renderer over results-fill-input.json and the disclosure record? Both need a merged, synthetically tested implementation before the unseal.","What replaces the Results cold gate for a renderer written after DLE-0: one executing reader plus validator (as the Paper 1 plan assumes), or a cold gate? Needs a deviation-log entry (DLE-4) signed blind.","Will the release event tie the second seal's digests (configs/analysis/b5/seal_pins.json, Erratum 1) or also the first seal's table in SEAL_RECORD §4.1? The registration §8.3 text names 'this file, the analysis plan and the catalog'; the dry-run record also carries erratum_2/3 digests.","Does the paper's production custody open for reported energies and claims have to run at the pinned commit, or does main's validator source still match the receipts after r4? If validators changed, the receipts refuse (paper_custody_receipt_binding_mismatch) and the dry-run custody documents must be regenerated blind.","Who is the designated blind repair seat after the event, and is that seat barred from reading the PR bodies and the rendered lines (registration §8 custody map, the two channels a path list misses)?","Should the second renderer output (released.txt) be renamed before block 6 to remove the early-unblinding trap, given it is written by L9 code pinned by the analysis commit (a cited rebind would be required for block 5; a block-6 change is free)?"]
# Block 5 release-to-paper path: Fable seat audit (2026-11-07)

**Seat.** Fable 5.1, audit track "Block 5 release-to-paper path". Independent of the Opus seat.
**Evidence base.** `origin/main` at `16c37a4bf` (worktree `/Users/edr/code/CapstoneProject/jw-wt/fable-b5-paperpath`, created from the canonical clone and removed at the end). Tag `b5/analysis-r3` = `654b9c8b3`. No restricted directory, night archive, `jw-b5-*` folder or custody was opened; no Block-5 value, difference, verdict or outcome word was read or inferred. Every citation is `path:line @ 16c37a4bf` unless another commit is named. No files were committed; nothing was merged; no PR or comment was made.

## 0. One-paragraph verdict

The pre-unseal release check (`scripts/release_b5.py`, DLE-1) is sound and well tested. **The path after it is almost entirely unwritten.** Specifically: (1) the "release event" the registration requires is still a placeholder in the seal record, with no template, no command and no stated ordering relative to opening restricted bytes; (2) there is no Block-5 Results renderer at all, so today every number in Paper 1 Part 1 would be copied by hand from restricted JSON into prose; the only mechanical binding that exists (D-173 custody plus `joulewise/paper_rendering.py`) covers reported energies and the two contrasts but has no production role for dominance ratios, floors or the §7.3/§8 disclosure sentences, and nothing calls those renderers outside tests; (3) the renderer obligation declared on 2026-10-20 (Q-RENDERER) depends on a "Results cold gate" that DLE-0 abolished, so a post-release renderer currently has no gate at all; (4) RS item 83 ruling 3's hand check of the uncovered step-11 leaves is manual with no worklist and no record format; (5) the registration's placement question Q4 is still open and D-174 still says the methods paper prints no `_v5` result, so printing anything needs an adoption ruling that nobody has scheduled; (6) several places let a person unblind early by accident, chief among them the disclosure producer's file named `<digest>.released.txt`, which holds the values, and the runbook's circular `PINNED` instruction. The ordered checklist in §6 fixes the order of operations and gives the commands.

## 1. What is in place (and what I checked)

- **`scripts/release_b5.py`** (`scripts/release_b5.py:1-506`): standard-library only; stage (a) re-hashes every dry-run output under `dry-run/restricted` without following links and every input-census row at the indexed roots using L9's own mapping (`:243-312`); refuses a dirty checkout (`:163-168`); pins the bar set by SHA-256 (`:58`, `:428`); routes recompute and comparator streams into `--restricted-out` only (`:315-318`); a final regex guard replaces any verdict whose bytes read as a decimal number (`:452-460`). Exit 0 only on `agree` (`:407-415`). Tests `tests/independent_recompute/test_release_b5.py` cover agreement, disagreement, tampered/missing/symlinked outputs, tampered inputs, FIFO hangs, wrong commit, changed pins/index, incomplete record, dirty checkout, STOP flag, restricted-out placement, CLI output and the identifier whitelist (`:159-427`).
- **Runbook** `docs/analysis/b5/RELEASE-RUNBOOK-lean.md`: the command (`:44-57`), the exit table (`:68-76`), the seven uncovered families (`:159-178`), the review record (`:180-207`).
- **Deviation log** `docs/analysis/b5/DEVIATION-LOG.md`: DLE-0 replaces plan step 12 (the results cold gate) by recompute agreement (`:46-72`); DLE-1 the release run (`:76-136`); DLE-3 r3 and the D5 release condition (`:200-320`), including the explicit statement that r3 is not releasable until D5 is answered and that an exit 3 is not §3.2 completion.
- **Dry run step 11** (`joulewise/b5_analysis/dry_run.py:1738-1762`): runs the disclosure producer and the fill-input builder, then records the flag `results_rendering_not_run_no_block5_template` (`:1759`). The renderer is never run.
- **Paper custody seam** (`joulewise/paper_custody.py`) and its renderers (`joulewise/paper_rendering.py:97-200`): `render_reported_energy`, `render_claim`, `render_d165`, each refusing anything that is not a verified production result, with fixed display precision (`:46-49`: 3 decimals J, 6 decimals J/token, estimates half-even, interval endpoints outward). The dry run exercises the production custody open for `claim_evidence` (step 9b, `dry_run.py:1571-1575`) and `reported_energy_parents` (step 10, `:1610-1613`) with `runs_root = <custody>/dry-run/restricted`, and writes the custody inventory/receipt documents (`:1311-1345`).
- **Supply map** `configs/paper_supply/supply_map.json`: three production roles only: `production.claim_evidence.gamma.v5` (two contrast subjects), `production.reported_energy_parents.qwen3-1p7b.v5`, `production.reported_energy_parents.qwen3-8b.v5`. `pending_roles` is empty. There is **no** production `d165_closeout` role and no floor role.

## 2. Findings: steps that are missing, manual or fragile

### F1 (HIGH). The release event has no template, no command and no stated ordering

- Registration §8 item 3 (`configs/campaigns/v5_claim_25g83/registration_block5.md:4842-4848`): after the blind dry run completes, "the lead records a **release event** tying the sealed SHA-256s of this file, the analysis plan and the catalog to the final harvest records; the analysis then runs exactly as registered", written as a section "Release event" appended to the seal record.
- The seal record's section exists and is empty: `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md:624-628` "Nothing is recorded here yet."
- Nothing in the repo produces it. `CANONICAL.md:47` says only "The release event itself follows the plan's release section and `RUN_STATE.md`." The runbook ends at "Ask Ed for the unseal OK" (`RELEASE-RUNBOOK-lean.md:70`).
- Consequence: the one act that legally turns restricted bytes into readable ones is an unscripted prose edit. It is easy to open a restricted file before the section is committed (the registration makes the record the precondition for reading), and easy to omit a binding (the dry-run record digest, the verdict digest, the window-index digest, the release-checkout commit, Ed's OK).
- What the section must tie (derived from registration §8.3, §12 and the dry-run record schema): the second seal's `sealed.*` digests (`configs/analysis/b5/seal_pins.json`, including `erratum_2_sha256`, `erratum_3_sha256`), the three analysed windows' `plan_id` and `harvest_record_sha256` (from the record's `windows[]`, equal to `configs/analysis/b5/analysed_windows.json`), the pinned analysis commit and its tag, the window-index SHA-256, the SHA-256 of `dry-run/B5-BLIND-DRY-RUN-RECORD.json`, the SHA-256 of `$OUT/verdict.json` and its `release_checkout.commit`, the bar-set digest, Ed's OK (Gmail message id and time), the signer and the blind statement. A template and the hashing commands are in §6 step 5.

### F2 (HIGH). No Block-5 Results renderer exists; every paper number is hand-copied today

- Plan §3.1 step 11 names `scripts/render_results_fills.py` and `--validate-rendered` as the output "validated Markdown" (`analysis_plan_block5.md:171`). The dry run declares `results_rendering_not_run_no_block5_template` (`dry_run.py:1759`), and the seal record's declared deviation of 2026-10-20 (`SEAL_RECORD.md:630-636`) says why: "the only renderer is the retired Window-A template".
- Confirmed in code: `scripts/render_results_fills.py` renders the 1.5B/7B template (`:975-990` builds `1p5B_*`/`7B_*` cells) and, when both floor windows pass, deliberately stops with `_supplier_unknown("[B_decode_claim_J]")` (`:987-989`); the `gamma` key is accepted but never read (`:956`, `:27`). The registered template `docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md` has no GAMMA contrast, Holm, kept-quad, attribution-floor or dominance sentence; the registry forbids a Qwen2.5 `_v4` artifact from supplying any prospective row (`docs/paper/results-fill-registry.md:60-63`).
- The D-173 route (`paper_custody` + `paper_rendering`) **is** mechanical and **is** exercised blind by the dry run, but: nobody calls `render_claim`/`render_reported_energy` outside tests (search of `scripts/` and `joulewise/` found no caller); there is no CLI; the output is a fixed one-line-per-subject form, not paper prose; and the receipts bind validator source digests, so the open must run from a clean checkout at (or validator-identical to) the pinned commit, which is on `origin/main` (`docs/contracts/paper_supply_custody.md:33-45`; `joulewise/identity_pins.py:834-861`).
- Everything else the plan prints (floors `floor_gate_j` with n and component census, the 8 R and 4 R_cm with numerators and denominators, the §7.3 ratio and per-token difference, every §8 disclosure line, the attribution-floor sentence) has no production role and no renderer. The disclosure producer renders the §8 lines (`joulewise/b5_analysis/disclosures.py:1351-1379`) into `<digest>.released.txt`, which is the nearest thing to a mechanically produced paper text, but no validator checks that a paper paragraph equals those lines.
- Consequence: "claims whose rendering is not mechanically bound to the released record" is, today, **all of them** in the prose sense. The paper's numbers would be transcribed by a human from `recompute.json`/step-11 JSON. RS item 83 ruling 2 ("the paper's printed digits come from the results-fill registry", `RUN_STATE.md:343`) points at a registry whose active rows are `RETIRED_FALLBACK` / `PROPOSED_STOP_FILL` (`results-fill-registry.md:1-40`; `analysis_plan_block5.md:695-712`).

### F3 (HIGH). The declared renderer obligation references a gate that DLE-0 abolished

- `SEAL_RECORD.md:632-636`: any Block-5 Results renderer written after release must print every row of the fill input's contrast census with its issued status, select none, have a validator checking row-for-row correspondence, and "**passes the Results cold gate** before any number it prints is used."
- `DEVIATION-LOG.md:46-52` (DLE-0): step 12, the Results cold gate, "is replaced by the independent recompute agreeing with L9 within the blind-fixed bars." The comparator compares step-11 leaves against the recompute; it cannot gate a renderer written after it ran.
- Consequence: a post-release renderer has no gate. Either DLE-0 must be amended to keep a narrow renderer gate (one executing reader + validator, consistent with the Paper 1 plan's "have the independent recompute's comparison table checked by one executing reader", `docs/strategy/2026-10-27-paper1-contingency.md:95`), or the Q-RENDERER obligation must be re-pointed. This is a deviation-log entry for the lead, before anything is printed.

### F4 (MEDIUM). The RS 83 ruling-3 hand check has no worklist, no record form and no blind preparation

- `RUN_STATE.md:344`: the 624 uncovered step-11 leaves (synthetic count) that the paper prints are "checked by hand against the recompute's restricted output by the post-release reader before it enters the paper". The runbook repeats it (`RELEASE-RUNBOOK-lean.md:171-175`) and the coverage audit names the sources for the seven families the recompute does not compute.
- The comparator writes the leaf list to `comparison.json` `coverage.uncovered_numeric` (`scripts/compare_b5_recompute.py:4013`), which is restricted. No step extracts it as a structure-only worklist before the unseal, so the reader will improvise after seeing values.
- Fix (blind, before unseal): a probe that prints only the leaf identifiers of `uncovered_numeric`, `nonfinite`, `unmapped` and `absent_sources` (no values), modelled on `docs/process_traces/2026-11-07-b5-release-trace/extract_blind.py:1-40`, run with `python3 -I`; then a check-record format: leaf id, paper location, source named by the coverage audit, reader, result. See §6 step 3.

### F5 (MEDIUM). The runbook's `PINNED` is circular, and nothing ties the pin to the tag

- `RELEASE-RUNBOOK-lean.md:38`: "`PINNED` ... It is the record's `analysis_commit`." `release_b5.py:275-276` then checks `record["analysis_commit"] == pinned`. If the operator copies the value from the record, the check is vacuous. The program also does not check that the pinned commit is the tagged analysis commit or an ancestor of HEAD (only that `seal_pins.json` is readable there, `:278-284`).
- Fix: `PINNED=$(git rev-parse b5/analysis-r4^{commit})`, taken from the tag, then require it to equal the record's value and `git merge-base --is-ancestor "$PINNED" HEAD`. DLE-3 says the rebind is "the tag and the re-run" (`DEVIATION-LOG.md:204-207`), so the tag is the authority.

### F6 (MEDIUM). Placement is unruled; D-174 forbids the print the Paper 1 plan assumes

- Registration §14 Q4 is open: "D-174's fallback places no `_v5` result; printing needs an adoption ruling" (`registration_block5.md:5968-5969`; `analysis_plan_block5.md:697-698` "no row below has a placement").
- `docs/paper/draft-v2-skeleton.md` is the methods/diagnostic paper; its selector accepts only `METHODS_DIAGNOSTIC` and rejects any result fill (`docs/paper/fill-rehearsal/branch-selection.md:1-25`). The placement proposal `docs/contracts/paper_comparison_placements.md` is "COMPLETE SPECIFICATION PROPOSAL / STOP_FILL" with X5 `RETIRED_FALLBACK` and every other row `PROPOSED_STOP_FILL` (`:3-35`).
- The Paper 1 plan (`docs/strategy/2026-10-27-paper1-contingency.md:86-96`) assumes "numbers drop into tables when each release happens" and "Results sections as templates bound to the results-fill registry". No such template exists for Block 5, and no decision supersedes D-174 (search of `docs/decision_log.md` found none).
- Consequence: the adoption ruling (which rows print, at which sites, with which adjacent limitation sentences) is a prerequisite that can be done blind now; done after unseal it is an outcome-informed choice.

### F7 (LOW). Minor fragilities in the release command path

- `release_b5.py` refuses any untracked file (`:166`); the analysis Air routinely has `.codex-report/` and scratch in checkouts. Use a fresh clone/worktree for the release.
- `INDEX` extraction when `analysed_windows.json` changed since `PINNED` (`RELEASE-RUNBOOK-lean.md:39`) is a manual `git show`; the index carries absolute roots, so any offload of an archive or runs root (the external SSD plan) before the release breaks stage (a) and violates the retention rule (`RUN_STATE.md:47`: nothing recorded in the ledger is moved before the release event).
- `--harvest-meter` is attached only when `withheld/meter.json` exists (`release_b5.py:335-336`); absence is silent. The verdict reports `meter_*` families only when compared; the reader should confirm three meter files were offered.
- `release_b5.py` records `release_checkout.commit` but not the SHA-256 of the dry-run record, `recompute.json` or `comparison.json`; the release-event section must hash them (§6 step 5).

## 3. Findings: places a human could unblind early

### U1 (HIGH). `<digest>.released.txt` holds the values

`scripts/produce_b5_disclosures.py:213-216` writes three files under `dry-run/restricted/disclosures/`: `<sha>.json` (record), `<sha>.unreleased.txt` (`released=False`: every restricted item prints "withheld until the release event", `disclosures.py:1351-1353`), and `<sha>.released.txt` (`released=True`: values and RESTRICTED codes). The word "released" in a filename invites an operator tracing a hold to open it as if it were the public view. The dry-run record names the roles `disclosure_released` / `disclosure_unreleased` (`dry_run.py:1751`), so a reader of the record alone could pick the wrong one. Mitigation (no code change needed before r4): the checklist says in words that `*.unreleased.txt` is the only view a blind seat may read, and the probe scripts refuse `released.txt`. A rename (`post-release.txt`) is a safe docs/code change for block 6.

### U2 (MEDIUM). "Trace the hold from `$OUT/comparison.json`"

`RELEASE-RUNBOOK-lean.md:71` and `:100` allow a blind seat to open `comparison.json` to trace a hold "structure-only". That file holds values, differences and bars. The r3 trace did it correctly through `extract_blind.py` (coarse buckets, types, reason words; `docs/run_reports/2026-11-07-b5-release-hold-trace.md:3-9`), but the runbook does not name the tool. Add: never `cat`/open; use `python3 -I docs/process_traces/2026-11-07-b5-release-trace/extract_blind.py "$OUT/comparison.json" <out>` and read only its output.

### U3 (MEDIUM). Ordering: opening before recording

Registration §8.3 makes the release event the precondition for reading, and the custody map says a seat that will write a post-release repair reads no restricted path even after the event (`registration_block5.md:4895-4904`). Nothing in the runbook orders "commit the release-event section, then open". §6 fixes the order and names the roles (opener, blind repair seat).

### U4 (LOW). Known terminal channels

The registration itself lists the three programs that print a science result on success (`registration_block5.md:4906-4911`: the close-out without `--output`, `analyze-claims`, `render_results_fills.py`), plus PR bodies that quote replays. Post-release renderers (`paper_rendering.render_*`) also print values; run them only after the event and only into restricted custody or the paper working copy. `release_b5.py`'s own stdout is structure only (`:494`), and the recompute's stdout prints only `sha256=... python=...` (`scripts/independent_recompute_b5.py:3234`).

### U5 (LOW). The verdict is structure; its surroundings may not be

`$OUT` is created 0700 outside the checkout (`release_b5.py:463-473`). The suggested location is a sibling of the custody root; if that parent is synced (Dropbox/iCloud), the values travel. Put `$OUT` under the same restricted parent as the custody root and nowhere synced.

## 4. Findings: what the paper may say (registration licence) and what would exceed it

Mechanically checkable constraints, each with its source, to be turned into a lint over the Paper 1 results text before any number enters it:

1. **Rungs.** ALPHA and BETA cells are L1 only; "ALPHA beside BETA" is side-by-side L1 "labelled as collected in separate windows in a fixed order", never a comparison (`registration_block5.md:1637-1643`; plan §12 "Treat the ALPHA-versus-BETA difference of reported means as a comparison" is forbidden, `analysis_plan_block5.md:766`). GAMMA contrasts are L2 **iff** `claim_evaluation.claim_ready_for_l2_l3` is true (`registration_block5.md:1641`; plan §7.2 `:444-470`); otherwise L1 wording. The claims-ladder forbidden words per rung (`docs/contracts/claims_ladder.md:69-73`): no "faster, cheaper, more efficient, scales, law, proves" etc.
2. **Both contrasts print whatever their status.** Q-RENDERER (`SEAL_RECORD.md:633-635`): every row of the contrast census with its issued status, unsupported and refused included; "selects none". A not-resolvable or not-estimable contrast prints as itself with null (D-190, `docs/decision_log.md:234`, `:12263`); "an unresolved or refused contrast is not equality or zero effect" (`docs/paper/figures-plan.md:119`).
3. **Dominance sentence and the "attribution-limited" subtitle** only on branch A (all 8 R and required R_cm at or above 2) (`analysis_plan_block5.md:357-358`; `registration_block5.md:1628-1631`); otherwise branch B with each failed component in null framing. Every ratio prints with numerator, denominator, n and "point diagnostic; no interval" (`:359-360`). R_cm passing licenses no physical-common-time robustness claim (`:353-355`).
4. **Fixed sentences** that must appear verbatim: the attribution-floor sentence beside each reported cell (`analysis_plan_block5.md:257`; `disclosures.py:33-37`), the gross-energy sentence beside the contrast (`:489-490`; `disclosures.py:39-40`), the conditionality sentence (`disclosures.py:50-52`), the D-177 limitation beside every phase-energy number (`registration_block5.md:1645-1646`; `docs/contracts/paper_comparison_placements.md:46-55`), and the §7.3 "registered descriptive estimates" label on ratio and per-token difference, with "timing bounds not propagated" (`analysis_plan_block5.md:481-487`).
5. **Never printed as the result:** the sensitivity line (`analysis_plan_block5.md:771`); any analysis not registered unless labelled exploratory (`:771-772`); a prompt-population claim, other prompt lengths, other machines, or wall power (`registration_block5.md:1645-1653`: boundary label `M3 Max / MLX / powermetrics SoC rails`; the meter is a descriptive cross-check, never a claim, `:1651-1653`, plan §8.2 `:646`).
6. **Printed precision** is the renderer's (`paper_rendering.py:46-49`), not the registry's retired rows; RS 83 ruling 2 should be re-pointed at it.
7. **Removed units** print with code, family, stage and ordinal; RESTRICTED codes may print only after the event (`disclosures.py:1354-1360`), and a unit removed by a RESTRICTED code in any pre-event text stays "removed (restricted code)".
8. **Seven families not recomputed** (monitor cost, arm hazards, battery, battery temperature, reference/corpus/NEG-8 history, attempt history incl. G10, selection): the paper may print them only after the ruling-3 hand check against the source the coverage audit names (`RELEASE-RUNBOOK-lean.md:159-178`; `docs/analysis/b5/LEAN-COVERAGE-AUDIT.md` §2).

Things the current drafts say that would need care: `docs/paper/draft-v2-skeleton.md:874-900` says no release/archive locator has issued; once Block-5 numbers print, the evidence-availability section must name the custody, the dry-run record digest and the release event, or the paper claims more reproducibility than it has.

## 5. Open design gap the lead should rule before unseal (not a defect, a decision)

Which of the two mechanical routes carries the paper: (a) extend D-173 custody with production roles for `d165_closeout` and the floors and write a small CLI around `paper_rendering.render_*`, or (b) write the Block-5 Results renderer the Q-RENDERER deviation describes, reading `outputs/results-fill-input.json` plus the disclosure record, with a row-for-row validator. Route (a) already has blind coverage from the dry run for two of three families; route (b) matches the declared obligation. Either way the renderer must exist, be tested on the synthetic fixture (`tests/independent_recompute/fullsize_window.py`; `docs/paper/fill-rehearsal/*-gamma-claim-verdicts.json`) and be merged **before** the unseal, or its author is an outcome-informed seat.

## 6. Ordered post-unseal checklist (with the pre-unseal steps it depends on)

Conventions: `CLONE` is a fresh, clean worktree under `/Users/edr/code/CapstoneProject/jw-wt/`; `CUSTODY` the r4 dry-run custody root; all runs `nice -n 19 taskpolicy -b python3.13 -B` with `TMPDIR` under `/private/tmp/jwburn-release`. Nothing below reads a restricted file before step 6.

**Step 0. Bindings (blind).**
```bash
cd /Users/edr/code/CapstoneProject/jw-wt/handoff && git fetch origin --tags
git worktree add --detach /Users/edr/code/CapstoneProject/jw-wt/b5-release origin/main
cd /Users/edr/code/CapstoneProject/jw-wt/b5-release
test -z "$(git status --porcelain --untracked-files=all)" || echo "checkout not clean"
PINNED=$(git rev-parse 'b5/analysis-r4^{commit}')                      # from the tag, never from the record
git merge-base --is-ancestor "$PINNED" HEAD && echo "pinned is on this history"
python3 -I - "$CUSTODY/dry-run/B5-BLIND-DRY-RUN-RECORD.json" "$PINNED" <<'EOF'
import json,sys; r=json.load(open(sys.argv[1]))
print("mode",r["mode"],"completed",r["completed_without_tooling_refusal"],"commit_matches_tag",r["analysis_commit"]==sys.argv[2])
print("windows",[(w["pack"],w["plan_id"]) for w in r["windows"]]); print("outcome_class_rows",[s["step"] for s in r["steps"] if s.get("status")=="outcome_class"])
EOF
INDEX=configs/analysis/b5/analysed_windows.json
[ "$(shasum -a 256 $INDEX | cut -c1-64)" = "$(python3 -I -c 'import json,sys;print(json.load(open(sys.argv[1]))["window_index_sha256"])' "$CUSTODY/dry-run/B5-BLIND-DRY-RUN-RECORD.json")" ] || { git show "$PINNED:$INDEX" > "$(dirname "$CUSTODY")/analysed_windows.json"; INDEX="$(dirname "$CUSTODY")/analysed_windows.json"; }
for p in alpha beta gamma; do echo "$p meter offered: $(python3 -I -c 'import json,sys,os;d=json.load(open(sys.argv[1]));print(any(os.path.isfile(os.path.join(e["archive_root"],"withheld/meter.json")) for e in d["attempts"] if e["pack"]==sys.argv[2]))' "$INDEX" $p)"; done
```
Also: confirm no `outcome_class` row other than a D-189 step-9b row; confirm D5 is answered per DLE-3 (`DEVIATION-LOG.md:296-320`) before running stage (c).

**Step 1. Release check (blind).**
```bash
OUT="$(dirname "$CUSTODY")/release-check-$(date -u +%Y%m%dT%H%MZ)"      # unsynced restricted parent
mkdir -p /private/tmp/jwburn-release && TMPDIR=/private/tmp/jwburn-release \
nice -n 19 taskpolicy -b python3.13 -B scripts/release_b5.py --custody "$CUSTODY" --window-index "$INDEX" \
  --pinned-commit "$PINNED" --restricted-out "$OUT" --workers 10 | tee "$(dirname "$CUSTODY")/verdict-stdout.json"; echo "exit=${PIPESTATUS[0]}"
```
Exit 0 and `verdict: agree` or stop. On a hold, trace only with `python3 -I docs/process_traces/2026-11-07-b5-release-trace/extract_blind.py "$OUT/comparison.json" "$OUT/blind-extract.json"`; never open `comparison.json`, `recompute.json` or any `*.released.txt`.

**Step 2. Pre-unseal rulings (blind, lead; deviation log, public).** (a) DLE-4: the renderer gate that replaces the Results cold gate for the Q-RENDERER obligation (F3). (b) Placement adoption for registration §14 Q4: which rows of plan §9 print, at which sites, with which fixed sentences (F6); a dated addendum, not an edit of sealed files. (c) The route of §5 and the renderer merged with its synthetic test. (d) Name the seats: the opener (lead), the post-release reader for ruling 3, and at least one seat that stays blind for any repair (`registration_block5.md:4902-4904`).

**Step 3. Hand-check worklist (blind).** Extract leaf identifiers only:
```bash
python3 -I - "$OUT/comparison.json" > "$(dirname "$CUSTODY")/uncovered-leaves.txt" <<'EOF'
import json,sys; c=json.load(open(sys.argv[1]))["coverage"]
for k in ("uncovered_numeric","nonfinite","unmapped","absent_sources"): print(k, len(c[k])); [print(" ",x) for x in c[k]]
EOF
```
Cross each leaf the adopted placement will print with the source named in `LEAN-COVERAGE-AUDIT.md` §2; prepare the check-record table (leaf, paper site, source, reader, result) empty.

**Step 4. Ed's OK.** Record the Gmail message id and timestamp. No restricted file is opened before step 5 is committed.

**Step 5. Release event (the unseal, in writing first).** Append to `SEAL_RECORD.md` "## Release event" with: date, signer, Ed's OK id; the `sealed.*` digests of `configs/analysis/b5/seal_pins.json` (second seal, Erratum 1) copied verbatim; the three windows (`pack`, `plan_id`, `harvest_record_sha256`) from the record; `PINNED` and the tag; `window_index_sha256`; the digests below; `release_checkout.commit` from `$OUT/verdict.json`; the blind statement verbatim ("The release event has not happened..." becomes "The release event is this entry; before it the signer had seen no Block 5 energy or outcome value").
```bash
shasum -a 256 "$CUSTODY/dry-run/B5-BLIND-DRY-RUN-RECORD.json" "$OUT/verdict.json" configs/analysis/b5/recompute_bars.json configs/analysis/b5/seal_pins.json "$INDEX"
git -c user.name=mpmdw -c user.email=edr@Edrs-MacBook-Air.local commit -m "b5: release event recorded (seal record §Release event)" ...   # push, PR, merge per merge authorization
```
Only after this commit is on `origin/main` do restricted files open, and only to the named opener.

**Step 6. Open, render mechanically, never transcribe.** From a clean checkout at `PINNED` (the receipts bind validator sources), with `runs_root=$CUSTODY/dry-run/restricted`:
```bash
python3 -I - <<'EOF' > "$(dirname "$CUSTODY")/rendered-lines.txt"
from pathlib import Path
from joulewise import paper_custody as c, paper_rendering as r
root=Path("<CUSTODY>/dry-run/restricted")
print(r.render_claim(c.open_paper_input(c.ClaimEvidenceRef(role="production.claim_evidence.gamma.v5", runs_root=root))))
for m in ("qwen3-1p7b","qwen3-8b"):
    print(r.render_reported_energy(c.open_paper_input(c.ReportedEnergyParentsRef(role=f"production.reported_energy_parents.{m}.v5", runs_root=root))))
EOF
```
(Run without `-I` only if the repo needs `sys.path`; run from the checkout root.) Then the Block-5 renderer adopted in step 2(c) over `outputs/results-fill-input.json` and the disclosure record `<sha>.json`, with its validator, into the paper working copy. The `.released.txt` view is the reference for every §8 line; the paper paragraph must equal it or cite the difference.

**Step 7. Ruling-3 hand check.** Fill the step-3 table for every printed uncovered leaf against `recompute.json` (where the recompute computes it) or the coverage audit's named source; commit the table beside the release event.

**Step 8. Licence lint before any text leaves the working copy.** Check §4 items 1-8 mechanically: rung from `claim_ready_for_l2_l3`; both contrasts present; dominance branch; fixed sentences present verbatim (grep for the `disclosures.py` constants); no forbidden ladder words (`scripts/claims_lint.py` for the ladder vocabulary); sensitivity line labelled; boundary label; D-177 note beside every phase-energy number; evidence-availability section updated.

**Step 9. Paper assembly gates that already exist.** `docs/paper/fill-rehearsal/select_outcome_branches.py --check-rendered` (currently only `METHODS_DIAGNOSTIC`; the adopted placement ruling must extend or replace it), `docs/paper/build/check_markdown.py`, `build_paper.py`; `scripts/check_paper_round7_artifacts.py` and `check_paper_replay_fence.py` for the historical fences (`docs/paper/round7/fill-checklist.md:55-75`).

**Step 10. Repairs after release.** Only by seats that read no released number, with a synthetic fixture, every other fixture byte-identical (plan §3.2 item 3, unchanged by DLE-1); labelled "produced after unblinding" otherwise.

**Step 11. Close.** `git worktree remove` the release worktree; RUN_STATE entry (by the lead, not this seat); CANONICAL.md row "Block-5 release (unblinding)" updated to point at the release-event section and the renderer.

## 7. Evidence index

- `scripts/release_b5.py:1-506`; `tests/independent_recompute/test_release_b5.py:159-427`
- `docs/analysis/b5/RELEASE-RUNBOOK-lean.md:24,38-40,44-57,68-76,100,159-178`
- `docs/analysis/b5/DEVIATION-LOG.md:46-72,76-136,200-320`
- `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md:150-200,257,339-360,415-490,695-712,759-772`
- `configs/campaigns/v5_claim_25g83/registration_block5.md:1613-1653,4824-4911,5968-5969`
- `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md:309-316,624-636`
- `joulewise/b5_analysis/dry_run.py:1311-1345,1571-1575,1610-1613,1738-1762,1956-1958`
- `scripts/produce_b5_disclosures.py:213-247`; `joulewise/b5_analysis/disclosures.py:33-52,1351-1379`
- `scripts/render_results_fills.py:27,954-1010,1090-1150`; `docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md:1-60,285-2555`
- `joulewise/paper_rendering.py:46-49,97-200`; `joulewise/paper_custody.py:35-36,637-721`; `configs/paper_supply/supply_map.json`; `docs/contracts/paper_supply_custody.md:1-70`
- `docs/paper/results-fill-registry.md:1-63`; `docs/contracts/paper_comparison_placements.md:1-60`; `docs/paper/fill-rehearsal/branch-selection.md`; `docs/paper/round7/fill-checklist.md`
- `docs/strategy/2026-10-27-paper1-contingency.md:15-30,86-96`; `docs/decision_log.md:11360-11380 (D-174),12251-12270 (D-189/D-190)`
- `RUN_STATE.md:334-345 (item 83),47 (retention)`; `CANONICAL.md:41-50,71-78`
- `docs/run_reports/2026-11-07-b5-release-hold-trace.md:1-20`; `docs/process_traces/2026-11-07-b5-release-trace/extract_blind.py:1-40`
- `scripts/compare_b5_recompute.py:3942-4013,4058-4067,4090-4091`

## 8. What this seat did not do

No tests were run (the audit is a reading of docs and code; the release tests were run by the PR #688 reviews and CI). No restricted or night path was listed or opened. No file was written to the repository; the worktree was removed. External sources: none opened.
~~~~

## Appendix B. Seat 2 report (Opus 5.5), verbatim

~~~~markdown
TOP: ["No post-unseal procedure exists for the DLE-1 path. The lean runbook stops at 'Ask Ed for the unseal OK' (RELEASE-RUNBOOK-lean.md:70) and SEAL_RECORD.md:626 'Release event' is still empty. The only unseal runbook (#648) and the only Results renderer (#652) are unmerged and written for the removed heavy release: the renderer requires B5-RELEASE-RECORD.json with mode 'release' (results_renderer.py:183-186, 265 @15dd5c8f7), so it refuses on DLE-1 custody.","After unseal the lead is no longer blind, so the choices the paper path needs must be made now, blind. Still open: the §14 Q4 placement (plan :697-699, 'no row has a placement'); D-174's expiry (decision log line 220, still 'open'); display precision (RS 83 ruling 2 points to a registry that has no Block-5 rule); reason-code wording; the gate that replaces the Results cold gate, which the Q-RENDERER obligation (SEAL_RECORD.md:635-638) still requires although DLE-0 removed step 12; and named hand-check sources. DLE-0 says the coverage audit names those sources (DEVIATION-LOG.md:63); it does not (LEAN-COVERAGE-AUDIT.md:105).","Paper 1 is not bound to the released record. Its 219 {{FILL}} ids (174 new) live only on the unmerged lane/2026-10-27-paper1-draft, which has no PR. Sources are assigned by id-prefix regular expressions in build_fill_index.py. There is no filler and no branch selector; abstract and conclusion sentences would be composed by hand after unseal; check_markdown.py only detects [PENDING] markers. CANONICAL.md still points to the frozen draft-v1.md.","Paper 1 states things the record contradicts. Line 655 gives Block 6's S-13 tolerance (1 mJ, half a digit) as 'registered'; Block 5's bars are 1e-6 relative and absolute, set by a lead ruling (recompute_bars.json, RS item 83 ruling 1). Line 643 says 'the registered analysis ran after' the release event; under DLE-1 the numbers are the blind dry run's. Lines 1222-1223 say the restricted data sat under an account no agent used; agents ran the dry runs and probes on the Air (RUN_STATE.md:465; release-hold-trace.md:18). Lines 1260 and 1364 say outcome sentences were 'fixed in the registrations before the data existed'; they were drafted on 10-27, after collection closed on 10-12. Lines 621 and 1240 say a changed file stops a session from starting; it is in fact code.executed_differs_from_sealed, which excludes the window at harvest. Lines 38 and 1255 say 'every printed quantity' was recomputed; seven families are not, and the load line is exempt.","The release condition cannot express a registered null outcome. compare_b5_recompute.py:217-222 makes any null DISAGREE, even both-null, and :2150-2154 compares the floor values of every resolution whatever its status. So any refused floor resolution or not-estimable contrast (the D-190 states) holds the release forever. No blind rule covers the case where r4 ends in a legitimate registered null, which plan §3.1 says 'is printed as such'.","The analysis-program addendum required before the release event (registration §11 item 4, :5519-5523) is missing from SEAL_RECORD. DLE-3 treats the tag as the pin. Under DLE-1 the programs that decide the release run from a later, unpinned checkout and need pinning too: release_b5.py, the recompute, the comparator and the bars. Only #655's unmerged r2 draft exists.","Blinding channels. (1) The blinded verdict copies per-family pass counts (release_b5.py:384-397). The comparator's loo_magnitude rows (compare_b5_recompute.py:3248-3260) exist once per quad that raises the leave-one-out magnitude trigger, so those counts carry a pass/fail derived from science energies, which registration §8 item 2 restricts. (2) The paper must disclose that floor-resolution status words of the GAMMA verdicts were read under a 'structural' ruling, and that D5b's relabel was ruled after that read (DEVIATION-LOG.md:234-236, 252-274). (3) The repo is PUBLIC and agent intake reads RUN_STATE first, so any released number committed anywhere unblinds the 'blind repair seats' that plan §3.2 item 3 relies on.","The custody route for paper inputs does not match the plan. Plan §1 item 3 requires D-173's open_paper_input, but supply_map.json has only three roles: claim_evidence.gamma needs a step-9b sidecar that D-189 says will not exist, and there are no roles for floors, the close-out or the disclosures. The governed receipt for prose that prints with no verdict (A145 CLAIM-NONISSUANCE-RECEIPT-01) is shelved. A deviation entry adopting reads bound to the record's digests is needed.","Fragile manual steps. Runbook line 66 says stdout and verdict.json are the same bytes; I ran it, and they differ (compact JSON vs indent=1; sha 77d56bf3 vs 2dd8384c). The verdict carries no digest of the dry-run record or of recompute.json/comparison.json. The registration §12 inventory-digest rule is manual; release_b5 checks 5 of the 8 sealed keys. The structure-only tracer extract_blind.py has no test and the runbook does not mention it. No first-reader log exists. The renderer imports comparator internals, so Ed's 'trim first' FREEZE-BY-COMMIT step can break re-rendering unless the tools run from tags.","A cheap fix exists. scripts/b5_e2e_synthetic.py runs the full synthetic chain in about 7 minutes, enough for a blind dress rehearsal of release check, then release event, frozen SHA256SUMS bundle, renderer, Paper 1 filler and validator. Paired with blind rulings, a DLE-1-compatible renderer port and a fill map from ids to JSON pointers, the post-unseal path becomes copy-only. The pre-unseal work is about 2-4 h of rulings and writing plus about 1 day of code, and can run in parallel with the r4 dry run."]
OPEN: ["Must Ed's unseal OK be written (an email id) and cited in the Release event, or is a verbal OK enough? DLE-1 requires the OK; the registration names only the lead as recording the event.","Which gate replaces the 'Results cold gate' that the Q-RENDERER obligation still demands for a post-release renderer (SEAL_RECORD.md:635-638), now that DLE-0 replaced step 12? Is one fresh executing reader, as in contingency plan §5, enough? That seat would also be the second licensed reader under registration :4901-4902.","Is D-174 expired by the Paper 1 plan, or does it need Ed's written instruction (decision log :11365-11367)? Until it is, every Block-5 registry row stays RETIRED_FALLBACK.","If r4 ends in a legitimate registered null state (a refused floor resolution, or a not-estimable contrast), should the comparator get a blind rule (both sides null with the same independently derived status word counts as AGREE)? Or is any null a permanent hold by design, contradicting plan §3.1's 'printed as such'?","Are the registered fixed sentences printed verbatim, internal names such as 'NEG-8 screen' included, or in the plain-language paraphrases the draft uses (DRAFT_NOTES Q5)?","Is Paper 1's new title acceptable under the registry's 'protocol-first title fixed before collection' and D-165's rule that 'attribution-limited' appears only as the branch-A subtitle?","Which document is canonical Paper 1: lane/2026-10-27-paper1-draft (a1a5029fb, no PR) or the PR #531 instrument-automation outline? Should the draft be merged before unseal, so its blind provenance is on main and tagged?","Will released numbers be kept out of the public repo, including branches, RUN_STATE and PR bodies, until repairs and the gate close, so that post-release repair seats can stay blind?","Who are the designated post-release readers: only the lead session, or also delegated Sol and Opus hand-check seats? Should the Release event name them, given registration §8's reader rule?","Should the public blinded verdict stop carrying per-family pass counts, starting with Block 6, given the loo_magnitude row-count channel? And should Block 5's paper disclose that channel?","Should FREEZE-BY-COMMIT-01, which Ed set as the 'first job after release', wait until the release bundle is frozen and the renderer and filler are tagged? Its phase-1 rehearsal would then re-run the paper rendering from the tags."]
## Block 5 from release to paper: Opus audit (2026-11-07)

**Seat.** Opus 5.5, audit track "Block 5 release-to-paper path". I worked alone, read-only, from a detached worktree of `origin/main` at `16c37a4bf` (removed when I finished). I also read these unmerged lanes with `git show`:
- `lane/2026-10-27-paper1-draft` at `a1a5029fb` (the Paper 1 draft; it has no PR);
- `lane/2026-11-05-b5-results-renderer` at `15dd5c8f7` (PR #652);
- `lane/2026-11-05-b5-release-runbook` at `08fe9e6cf` (PR #648);
- `lane/2026-11-05-b5-release-readiness` at `836548931` (PR #655).

**Blinding.** I opened no custody, archive, `night-*`, `jw-b5-*` or `restricted/` path. I worked out no Block-5 value or verdict. Where this report quotes the deviation log's own structural statements, it draws no inference from them about any result.

**What I ran.** One run of `scripts/release_b5.py`, against an empty fake custody under `/private/tmp`, to check the verdict's bytes. It touched no real data.

**Citations.** Paths are at `main@16c37a4bf` unless another commit is named. Paper 1 lines are `docs/paper/paper1/paper1.md` at `a1a5029fb`. I opened no external URLs.

---

## 0. Summary

After the release check prints `agree`, nothing on `main` says what happens next.
- The lean runbook ends at "Ask Ed for the unseal OK" (`docs/analysis/b5/RELEASE-RUNBOOK-lean.md:70`).
- The seal record's "Release event" section still reads "Nothing is recorded here yet" (`docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md:626`).
- The only unseal runbook (#648) and the only Block-5 Results renderer (#652) are unmerged. Both target the heavy `--mode release` run that DLE-1 removed.
- Paper 1 is unmerged, has no PR, and has no program that fills its 219 placeholder ids.
- Several Paper 1 sentences contradict the record: the tolerance, when the analysis ran, who could touch the data, and when the outcome text was fixed.

The most important structural point: **after unseal, the lead is no longer blind.** Ed's delegation of prereg rulings to the lead covers blind rulings only (DEVIATION-LOG.md:30-31). The plan also lets only seats that have read no released number write or review a repair after release (analysis_plan_block5.md:196-199). So every choice the paper path needs has to be made before the release event:
- placement;
- display precision;
- reason-code wording;
- the gate that replaces the Results cold gate;
- the hand-check sources;
- the branch selector;
- the abstract variants;
- the custody route.

Afterwards, only a mechanical copy should happen.

---

## 1. What exists after `agree`

| Need after `agree` | What exists | State |
|---|---|---|
| Release-event procedure (registration §8.3, `registration_block5.md:4843-4848`) | Lean runbook §2 ends at "Ask Ed for the unseal OK". #648 `docs/process/b5_release_runbook.md` | #648 unmerged and stale: r2, `run_b5_analysis.py --mode release`, `B5-RELEASE-RECORD.json` |
| Release-event record | `SEAL_RECORD.md:624-628` | Empty; no template for DLE-1 |
| Analysis-program addendum before the event (registration §11 item 4, `:5519-5523`) | #655 `docs/process/b5_r2_analysis_addendum_DRAFT.md` | Unmerged r2 draft. DLE-3 treats the tag as the pin (DEVIATION-LOG.md:231-233) |
| Results renderer (seal-record obligation Q-RENDERER, `SEAL_RECORD.md:631-638`) | #652 `joulewise/b5_analysis/results_renderer.py`, `scripts/render_b5_results.py` | Unmerged; requires `B5-RELEASE-RECORD.json` with `mode == 'release'` (results_renderer.py:183-186, 265 at `15dd5c8f7`). It refuses on DLE-1 custody |
| Step-11 fill input | `scripts/build_results_fill_input.py`, `joulewise/results_fill_adapter.py` | GAMMA contrasts only. ALPHA/BETA carry identity only: plan_id, attempt, claim_usable and two digests (build_results_fill_input.py:83-85; results_fill_adapter.py:183-190). Reported cells, floors and ratios come only from the disclosure record and the projections |
| Old renderer `scripts/render_results_fills.py` | Window-A template | Retired by Q-RENDERER; do not use |
| Paper text | CANONICAL.md "Paper" points to `docs/paper/draft-v1.md` (frozen; draft-v1's own README calls it frozen) and the Window-A registry | Stale. The Paper 1 draft is only on `lane/2026-10-27-paper1-draft`, with no PR. A second "PAPER-1" outline sits on #531 |
| Paper 1 fill | `docs/paper/paper1/fill_index.md` + `build_fill_index.py` | Index only. Sources are assigned by regular expressions on id prefixes (build_fill_index.py `source()`). No filler, no branch selector |
| Paper build checks | `docs/paper/build/check_markdown.py` | Knows only `[PENDING…]` markers (`:26`), not `{{FILL:…}}` |
| D-173 custody for paper inputs (plan §1 item 3, `analysis_plan_block5.md:61-62`) | `configs/paper_supply/supply_map.json` | Three roles only: `claim_evidence.gamma.v5`, which needs the step-9b sidecar that D-189 says will not exist, and two reported-energy-parent roles. No role for floors, the close-out or the disclosures |
| Claim status for readers | `CLAIMS_STATUS.md` | Last updated 2026-08-20 |

---

## 2. Findings

### 2.1 Missing, manual or fragile steps

**F1. No post-unseal procedure for the DLE-1 path (BLOCKER for an orderly unseal).**
- DLE-1 replaced the heavy release run.
- #648's unseal steps (§§3-5) and its post-check script assume `release/B5-RELEASE-RECORD.json`.
- #652 refuses without it.
- Nothing says the release event must be recorded *before* anyone reads values.
- The runbook says "Do not open these before the unseal OK" (`RELEASE-RUNBOOK-lean.md:100`). The registration, though, makes the recorded event the boundary, not the OK.

**F2. The rulings the paper path needs are all still open. After unseal they cannot be made blind.**
1. **Placement (registration §14 Q4, `:5968-5969`).** The plan says "no row below has a placement; each becomes printable only through the placement ruling of registration §14 Q4" (`analysis_plan_block5.md:697-699`). D-174 is still "open" (`docs/decision_log.md:220`). It expires only "at submission or on Ed's written instruction" (`:11365-11367`). Every Block-5 site of Paper 1 is `PROPOSED_STOP_FILL` or `RETIRED_FALLBACK` (fill_index.md fill rule; DRAFT_NOTES.md point 2).
2. **Precision.** RS item 83, ruling 2 says printed digits "come from the results-fill registry" (`RUN_STATE.md:343`). The registry has no active Block-5 precision rule. #652 says so itself: "NEEDS-LEAD: bind each final site's registry precision" (`b5_results_renderer.md:139-142` at `15dd5c8f7`). Choosing rounding after seeing the numbers is discretion.
3. **The gate that replaces the Results cold gate.**
   - Q-RENDERER says a post-release renderer "passes the Results cold gate before any number it prints is used" (`SEAL_RECORD.md:635-638`).
   - DLE-0 replaced step 12 (the cold gate) with the recompute (DEVIATION-LOG.md:38-49).
   - The recompute does not check rendered Markdown. So nothing now names who checks the renderer's output.
   - The registration also names "the results cold gate" as one of the only two readers allowed after the event (`registration_block5.md:4901-4902`).
4. **Hand-check sources for the seven families the recompute does not cover.** DLE-0 says the hand check "needs another source, which that audit names" (DEVIATION-LOG.md:63). The audit names none: "needs another derivation/source check; it cannot compare two nonexistent values" (`LEAN-COVERAGE-AUDIT.md:105`). Also uncovered:
   - the load-correlated line, which is recomputed but exempt (`LEAN-COVERAGE-AUDIT.md:86`);
   - the reason-code words that choose between `not_estimable` and `not_resolvable` ("Partial: … no full reason-code evaluation", row "Outcome, direction…").
5. **Wording.** Plain-language glosses for every registered refusal code are unsettled, and so is whether registered fixed sentences may be paraphrased (DRAFT_NOTES.md open question 5).
6. **The paper tier** (contingency plan §2-3). It must be recorded by date and completion before any value is read.

**F3. The analysis-program addendum is missing, and DLE-1 widened what must be pinned.**
- Registration §11 item 4 requires an addendum to the seal record before the release event. It names "the files and their SHA-256s and the desk checkout's commit", written by a blind seat (`:5519-5523`).
- The seal record has addenda 1-5 for the harvest, the errata and the meter. It has none for the analysis code.
- Under DLE-1, three programs decide the release, and they run from a *later* clean checkout: `release_b5.py`, `independent_recompute_b5.py` and `compare_b5_recompute.py`, with `recompute_bars.json`. That checkout is recorded only as `release_checkout.commit` inside a restricted-folder file.

**F4. A registered null outcome can never give `agree`.**
- `Comparison.numeric` makes any null on either side DISAGREE, including both sides null (`scripts/compare_b5_recompute.py:217-222`).
- `compare_arms` compares `floor_abs_j`, `floor_cmp_j` and `floor_gate_j` for every resolution whatever its status (`:2150-2154`).
- A refused resolution must carry null values (D-190 item 3). So any refused floor resolution, tooling-class or registered, holds the release for ever. A not-estimable contrast's null estimate does the same.
- #652 already flagged this (`b5_results_renderer.md:150-157`).
- For D5, DLE-3 makes it a hold by design (DEVIATION-LOG.md:330-347). But no blind rule says what happens if r4 ends in a *legitimate* registered null. Plan §3.1 says such an outcome "is the result and is printed as such".

**F5. The custody route for paper inputs does not match the plan.**
- Plan §1 item 3 requires D-173's `open_paper_input(role, runs_root)`.
- The supply map cannot supply floors, the close-out or the disclosures.
- Its claim-evidence role needs a sidecar that step 9b does not issue (D-189 item 4).
- #652 instead reads files bound by the record's digests. That is a sound route, but it needs a deviation entry adopting it.
- TASK_QUEUE A145 `CLAIM-NONISSUANCE-RECEIPT-01`, the governed route for prose that must print with no verdict, is SHELVED (`TASK_QUEUE.md:1254`).

**F6. Post-release work deferred to seats that must be blind.**
- Several items are deferred "to after the release": a D-178 successor with explicit non-issuable rows, and the step-11 code registration and related cleanups (`RUN_STATE.md:1025-1026`, item 165).
- So is FREEZE-BY-COMMIT-01, which Ed set as the "FIRST job after the block-5 release" (`RUN_STATE.md:1032-1043`).
- After unseal, plan §3.2 item 3 lets only blind seats write or review such changes. Paper-issuance work (the renderer port, the D-178 successor) is cheaper to finish before unseal.
- The trim must not run until the paper's inputs are frozen and the tools are tagged. The renderer imports comparator internals (`b5_results_renderer.md:60-65`).

**F7. Smaller fragile points.**
- (a) The runbook says the stdout verdict and `$OUT/verdict.json` are the same bytes (`RELEASE-RUNBOOK-lean.md:66`). They are not:
  - `finish()` writes compact JSON (`scripts/release_b5.py:454-459`), while `main()` prints with `indent=1` (`:494`).
  - My fake-custody run gave stdout sha `77d56bf3…` and verdict.json sha `2dd8384c…`.
  - Cite the file's digest.
- (b) The verdict carries no digest of the dry-run record or of `recompute.json`/`comparison.json`. The release event would have to compute them by hand.
- (c) Registration §12 (`:5687-5700`) requires the harvest-recorded digests of the registration, catalog *and inventory* to equal the seal record. `release_b5` checks only five sealed keys (`release_b5.py:73-75`); `seal_pins.json` has eight. The rule is manual and belongs in the release-event checklist.
- (d) The structure-only tracer used for holds, `docs/process_traces/2026-11-07-b5-release-trace/extract_blind.py`, lives in process traces. It has no test, and the runbook does not mention it (the runbook says only "A blind seat traces … from `$OUT/comparison.json`", `:71`).
- (e) The runbook still names dry-j and dry-k and the lane branch (`:37`, `:45`).
- (f) No written record exists of who first read released numbers, or when, so repair seats cannot show they were blind. #652's review file has `reader` and `first_read_utc` fields, but it is unmerged.
- (g) The contract `docs/contracts/paper_comparison_rendering.md`, which #652 cites, was removed by the prune (`71dea4e09`). It survives only in the archive tag.

### 2.2 Rendering not mechanically bound to the released record

**R1. No Paper 1 placeholder is filled by a program.** There are 236 occurrences of 219 ids; 174 ids are new (fill_index.md header). Two examples of how loosely sources are assigned:
- Every `P1-B5-*` id gets the same source, "primary-block analysis outputs and disclosure producer (§4-§8)", rather than an artifact and JSON pointer.
- The attribution floors `P1-B5-AF-*` should bind `binding.attribution_floor_j` of the step-10 projection; the index gives the generic source.

**R2. Branch selection is manual.** Sections 5.1.a, 5.2.a, 5.4.A/B/R, 5.5.1-5.5.5, 5.7.x and 9.B-9.D all need a branch chosen. The issued fields that should choose them are:
- `claim_evaluation.outcome`, `direction`, `claim_level_ceiling`;
- the leave-one-quad-out influence flag;
- the close-out `branch`, `dominance_sentence_licensed` and `subtitle_licensed` (`docs/contracts/d165_dominance_closeout.md:445-446`).

A wrong choice overclaims, for example picking 5.5.1 when the ceiling is L1. The old selector's design ("single-outcome validator/copier", results-fill-registry.md:12-14) should be repeated.

**R3. Composite sentences are written after release.** These are assembled by hand from outcome ids after unseal: `P1-ABS-PART1` (abstract), `CP-X08-*-conclusion`, `P1-RECOMPUTE-SUMMARY` and the 5.5.4 reason text. That is where spin enters. They should be pre-written now as a finite grid of variants.

**R4. Reason texts are free-form.** `P1-B5-CTR-NR-REASON` includes the free-text option "no floor could be issued" (paper1.md:806). After D5b, a floor-binding refusal is `floor_artifact_invalid`, which is `not_estimable` (DEVIATION-LOG.md:252-265), not "not resolvable". The reason must be rendered from the issued code through a gloss table fixed blind.

**R5. `P1-RECOMPUTE` and `P1-RECOMPUTE-SUMMARY` have no producer.** No program summarizes `comparison.json` per family. And the index's source names the wrong bars: "tolerance from docs/registrations/block6_replication_DRAFT.md §12.3".

**R6. #652 covers only the contrast table and the disclosures.** It writes a candidate `Results.md` with leaf provenance. Paper 1's Tables 1-5 are separate and would be transcribed by hand from it.

**R7. Nothing ties reading to the record after verification.** Files read later are not re-checked against the verified digests. Freeze a bundle with `SHA256SUMS`, and have every filler re-check (checklist D).

### 2.3 Where someone could be unblinded early, or stop being blind

**U1. The blinded verdict's counts can carry outcome-derived information.**
- `release_b5` copies the comparator's per-family `pass`/`fail` counts and `step11.uncovered_numeric` into the public verdict (`release_b5.py:384-397`).
- In `compare_disclosures`, the `loo_magnitude` rows exist for each quad that either side selects as raising the leave-one-quad-out magnitude trigger, the movement above a quarter of the floor (`compare_b5_recompute.py:3248-3260`). So the `contrast_j` and `outcome_word` pass counts grow with the number of such quads.
- That number is a "pass/fail derived from a science energy", which registration §8 item 2 restricts until the release event.

Recommendations:
- For Block 5, disclose this channel.
- For Block 6, print only agree or hold per family, or fixed-cardinality rows. Counts would appear only on a hold, for the blind trace.

**U2. A structural read that selects an outcome class must be disclosed.**
- DLE-3 records that the lead ruled floor-resolution status and reason words structural and read them on the dry-j custody (DEVIATION-LOG.md:234-236; `docs/run_reports/2026-11-07-b5-release-hold-trace.md:18-19`).
- D5b then changed which reason those refusals map to (DEVIATION-LOG.md:252-274).
- A resolution's status selects among registered outcome classes (plan §7.2).

The paper must state both: that this read happened before release, and that D5b was ruled after it. I draw no inference about any verdict.

**U3. Human-readable full results already sit in custody.** Step 11 writes `disclosures/<sha>.released.txt`, the full view (dry_run.py:1751; `disclosures.py:1351-1378`). #652's `--preview` produces full values. Both are guarded only by rule. Make the renderer refuse unless the seal record's "Release event" section names this record's SHA-256.

**U4. After unseal, the "blind repair seat" is fragile.**
- The repo is public (`gh repo view`: `PUBLIC`).
- Agent intake starts by reading `RUN_STATE.md`.
- So any number committed to any branch, RUN_STATE, run report or PR body reaches the next fresh seat.
- The registration already warns about PR bodies (`:4906-4912`).

Rule: keep released numbers out of git (in custody and the bundle) until repairs and the gate close. Repair briefs carry structure only.

**U5. Reader set.** After the event, restricted paths may be read only by "the lead, and the results cold gate" (`registration_block5.md:4901-4902`). Delegating hand checks or rendering to Sol or other seats widens that set. The release event should name the readers.

**U6. Programs that print results to the terminal.** `analyze-claims`, the close-out without `--output`, and `render_results_fills.py` print a result on an ordinary run (`registration_block5.md:4908-4912`). After unseal, blind seats must not run them on real custody.

### 2.4 What Paper 1 says that the registration or the record does not license

All lines are `paper1.md` at `a1a5029fb`.

| # | Paper text | Problem | Fix |
|---|---|---|---|
| P1 | 655-656: "The registered agreement tolerance is that each run's phase energy agrees within 1 mJ and every printed quantity … within half a unit of its last printed digit" (and 895) | That is Block 6's S-13 set. Block 5's bars are 1e-6 relative and 1e-6 J absolute, with counts exact (`configs/analysis/b5/recompute_bars.json`, sha `2f65bba2…`, = `RELEASE_BARS_SHA256`). They were bound by a lead ruling, RS item 83 ruling 1 (`RUN_STATE.md:342`), and adopted in DLE-0, not by the registration | Print the Block-5 bars per family; say "fixed blind before release (DLE-0)" |
| P2 | 643: "A release event then tied the digests …; the registered analysis ran after it" | Under DLE-1 the printed numbers are the blind dry run's outputs, made *before* the event and verified byte for byte (DEVIATION-LOG.md:96-110). Registration §8.3 and plan §1.1 said otherwise; DLE-1 is the deviation | State the DLE-1 order and list it in `P1-DEV-LIST` |
| P3 | 38 and 91: "an independent recomputation of every headline number from the raw records"; 653-656 and 1255: "every printed quantity" | Seven families are not recomputed. The load line is recomputed but exempt. The recompute takes the recorded judgments as inputs: anchors, calibration fits, exclusions (re-run), clean NEG-8 membership and screen decision (`LEAN-COVERAGE-AUDIT.md` §2, §3, §4) | "headline numbers … from the raw power records, with the recorded collection-time judgments as inputs"; list the uncovered families as hand-checked |
| P4 | 1222-1223: "A second laptop held the restricted data … under an account no agent used. Cloud machines … never held real or blinded data" | Agents ran the dry runs and the probes on the Air under the same account (`RUN_STATE.md:465`; release-hold-trace.md:18). Custody "is kept by rule, not by the file system" (`registration_block5.md:4853`). Development and local Sol also ran on the Air | Describe custody-by-rule and structure-only probes honestly |
| P5 | 1260-1262 and 1364: "Every sentence … is fixed in the registrations" / "fixed … before the data existed" | The branch prose was written in the draft on 2026-10-27 (`a1a5029fb`). Collection had closed on 2026-10-12 (`RUN_STATE.md:16`). Only the plan's fixed sentences are registered | "written before release, at commit …"; tag that commit (checklist A7) |
| P6 | 621 and 1240: "a session refuses to start if any file it reads differs from the sealed bytes" | A code difference raises `code.executed_differs_from_sealed`, EXCLUDE_WINDOW at harvest (flag_catalog.json; `registration_block5.md:1547`, `:3948`). The only identity refusal at the arm is the OS build and machine model (§4.7, `:2602`). HARVEST_FAULT covers changed *seal documents* only | Correct the mechanism |
| P7 | 629: "No registered arithmetic was changed after data existed (P1-DEV-LIST)", with the source list "seal record, replication §17, BYTES addenda" (fill_index) | The source list omits `docs/analysis/b5/DEVIATION-LOG.md` (DLE-0..3: release procedure, D1 printed key, D5b outcome-label mapping) and D-188..D-190. D5b changes which registered outcome word prints | Add those sources; describe D5b as a blind post-collection change to the reason mapping |
| P8 | 634-635: "no person or AI agent read … outcome word" | True for words, but U2's structural status read must be disclosed beside it | Add the disclosure |
| P9 | 717-718: `P1-B5-B-SHARE` "B ÷ (h + B)" | Not a formula the plan names. "Every printed number is MEASURED or DERIVE" (`analysis_plan_block5.md:713`); unregistered analyses are exploratory (registration §8.3) | Drop it or label it exploratory |
| P10 | Title (19): "…Attribution Limits…" | The registry fixed a protocol-first title before collection: "JouleWise: Timing Sensitivity of Phase-Energy Assignments on Apple Silicon". "Attribution-limited" may appear only as the branch-A subtitle (results-fill-registry.md:309-317) | Rule blind now (DRAFT_NOTES Q1) |
| P11 | 806 and §9.C (1377-1379): "not resolvable … a finding about resolution" | Must not be applied to `not_estimable`. D-178/D-189: non-issuance "is not an empirical negative result" | Gloss table with a branch per code |
| P12 | `P1-RECOMPUTE` source: "tolerance from block6 … §12.3" | Wrong bars (see P1) | Fix the fill_index source |

A small point that is consistent: §5.2's per-token caption ("512 runtime-observed output tokens, 511 of them generated in the decode phase") matches plan §4 step 6. Branches 5.5.1-5.5.3 and §3.10 match plan §7.2's order of precedence.

---

## 3. Registered quantity, paper site and binding

| Plan quantity | Issuing artifact and field | Paper 1 site | Bound today | Independent check | Action |
|---|---|---|---|---|---|
| Identity, workload, L = 2048 (§9 row 1) | selection record, prompt pin, panel, `identity_pins.json` | CP-X01-identity/length, P1-ID-OS | manual | partial: routing only, no re-selection (LEAN §2.7) | Check SHA-256 against the seal record |
| Reported cells: mean, lower, upper, J/token, n_r, n_b (§4) | step-10 `outputs/projection-<pack>.json` | Table 2, E_* | manual | compared (`reported_cell_j`, `per_token_j`, `count`) | Pointer map; precision rule |
| Attribution floor, attaining member (§4.7) | projection `binding.attribution_floor_j`, record | Table 2, P1-B5-AF-*, INTERVAL-PARTS | manual, generic source | values compared; `attained_by` uncovered | Pointer map; hand-check the member id |
| B share | not registered | P1-B5-B-SHARE | — | — | Drop or label exploratory |
| Floors abs/cmp/operative, n (§5) | aggregate floor artifact, extraction reports | Table 3, F_* | manual | compared (`floor_j`, `floor_gate_j`) | The filler checks operative = max = `floor_gate_j` |
| R, R_cm, terms, branch, subtitle (§6) | `closeout.json`, ratio table | Table 4, 5.4.*, CP-X02, 9.D | manual branch | compared, including `dominance_branch` | Bind the branch and subtitle to the close-out flags |
| Contrasts: d̄, metrology and decision intervals, floor gate, Holm p, outcome, ceiling (§7) | `outputs/claim-verdicts.json`, `outputs/results-fill-input.json` | Table 5, 5.5.*, abstract, 9.C | #652 candidate; Paper 1 manual | compared; reason codes not re-derived | Branch selector; gloss table; hand-check reason codes |
| Leave-one-quad-out, magnitude concern (§7.2, §8.1) | verdict `loo`, disclosure | P1-B5-CTR-LOO | manual | compared | Map |
| Ratio and per-token descriptive estimates (§7.3) | disclosure record | P1-B5-RATIO-*, PERTOK-* | manual | compared (log internals exempt) | Map |
| Battery-assist lines (§8.1) | sensitivity, disclosure | P1-B5-BATT-LINE, CTR-BATT | manual | values compared; status text uncovered | Map |
| Load-correlated line (§8.1) | sensitivity, disclosure | P1-B5-LOAD-LINE | manual | **not compared** (`LOAD_LINE`) | Hand-check against `recompute.json` load block |
| Kept and removed units, positions (§8.1) | disclosure cells, floors, contrasts | Table 1 | manual | core counts compared; positions exempt | Hand-check positions |
| Attempt history, G10 (§8.1) | disclosure block lines, window index | P1-B5-ATTEMPTS, P1-LEDGER | manual | **not recomputed** (index only) | Hand-check against `harvest.json` (releasable) |
| Arm hazards, physics counts, anchors, busy CPU, battery window and phase counts, thermistor (§8.1) | disclosure window lines | P1-B5-HAZARDS | manual | **not recomputed** | Name sources: `hazards/arm.json`, monitor journals, `derived/` files |
| Monitor cost (§8.1) | disclosure | P1-B5-MONITOR | manual | **not recomputed** | Name the source |
| NEG-8 census and terms (§8.1) | disclosure, `derived/neg8-*.json` | P1-B5-NEG8 | manual | gross terms compared; census not | Hand-check the census |
| Cross-window check (§8.1) | disclosure | P1-B5-XWIN | manual | compared | Map |
| Decision interval against the floor (§8.1) | disclosure text | P1-B5-CTR-DIFLOOR | manual | operands only | Hand-check the sentence |
| Whole machine (§8.2) | disclosure, `withheld/meter.json` | P1-B5-METER | manual | numbers compared; k/n and words text only | Hand-check k/n |
| Fixed sentences (§8.1) | disclosure fixed sentences | inline text, Appendix C | paraphrased | text uncovered | Rule verbatim or paraphrase |
| Recompute agreement | `comparison.json` | P1-RECOMPUTE(-SUMMARY) | none; wrong bars | — | Summarizer with the Block-5 bars |
| Release event; deviations | seal record; DEVIATION-LOG; D-188..190 | P1-RELEASE, P1-DEV-LIST | none; source list incomplete | — | Write the event; fix the sources |

---

## 4. Ordered checklist with commands

Variables used throughout:
- `$CUSTODY`: the r4 dry-run custody root.
- `$INDEX`: the window index the dry run read.
- `$PINNED`: the r4 analysis commit.
- `$REL`: the `--restricted-out` of the release check.
- `$RCHK`: the commit `release_b5.py` ran from.
- `$BUNDLE`: the frozen release bundle.

Items marked **(build)** do not exist yet.

### A. Before the release event, while the lead is still blind (can run in parallel with the r4 dry run)

**A1. Record the paper tier by date and completion** in RUN_STATE (contingency plan §3). Do not leave it open until numbers are read.

**A2. Rulings, written blind as DEVIATION-LOG entries (DLE-4 onward) plus a D-174 addendum:**
1. The Q4 placement decision: adopt or STOP each Paper 1 / CP-X site, mapped to a plan §9 row.
2. D-174's expiry (Ed's written instruction, or a dated addendum).
3. The custody route for paper inputs: the bundle bound by the record's digests replaces `open_paper_input` for Block-5 paper inputs, with the claim-evidence role inapplicable under D-189.
4. Display precision per family, with intervals rounded outward.
5. The gate for post-release rendering that replaces the Q-RENDERER cold gate. My recommendation: one fresh executing reader re-runs `--validate-rendered`, checks a sample of leaves against `$BUNDLE`, and checks the paper against the table in §2.4.
6. A named hand-check source per uncovered family (§3 table).
7. Verbatim or plain-language fixed sentences.
8. The comparator's handling of a both-null registered state (F4), if r4 can end in one.
9. The title against D-165.

**A3. Correct Paper 1** (§2.4 items P1-P12). Merge it, or at least open its PR. Point `CANONICAL.md`'s "Paper" rows at it and retire the draft-v1 and Window-A rows.

**A4. Pre-write blind:**
- the abstract and conclusion variants for every combination of outcome word, ceiling, dominance branch and replication word;
- the gloss table for every registered `not_estimable` and `not_resolvable` code and every refusal code;
- the branch-selector table.

**A5. (build) Port #652 to DLE-1 inputs and add a Paper 1 filler.**
- Change the renderer's inputs to `--bundle $BUNDLE` (or `--custody` plus `--release-verdict`).
- Add a refusal unless the seal record's "Release event" section names the record's and the verdict's SHA-256.
- Write `docs/paper/paper1/fill_map.json`: id → (bundle file role, RFC 6901 pointer, transform, precision).
- Write `fill_paper1.py`: it fills from the renderer's `provenance.json`, selects branches from issued fields, and refuses any unmapped id.
- Add a `{{FILL:` pattern to `check_markdown.py`.

**A6. Synthetic dress rehearsal of the whole path after the release check** (about 10-20 minutes on the Air, blind):

```sh
TMPDIR=/private/tmp/jwb5-rehearse/tmp nice -n 19 taskpolicy -b python3.13 -B scripts/b5_e2e_synthetic.py \
  --scratch /private/tmp/jwb5-rehearse/run --out /private/tmp/jwb5-rehearse/out --workers 7 --keep-custody
# then release_b5.py on the synthetic custody (window index via tests/independent_recompute/fullsize_window.py),
# then steps C4-E2 below unchanged, on synthetic data
```

**A7. Pins and tags.**
- Append the analysis-program addendum to `SEAL_RECORD.md`. Start from #655's draft. It must cover the r4 tree and the release-check commit's `release_b5.py`, recompute, comparator and bars:

```sh
R4=$(git rev-parse 'b5/analysis-r4^{commit}')
git ls-tree -r --name-only "$R4" -- joulewise scripts configs/analysis/b5 pyproject.toml env/analysis-lock.txt |
  while read -r f; do printf '%s  %s\n' "$(git show "$R4:$f" | shasum -a 256 | cut -d' ' -f1)" "$f"; done \
  > /private/tmp/b5-r4-program-files.sha256
```

- After B, tag the release-check commit and the blind Paper 1 commit:

```sh
git tag -a b5/release-check-r4 "$RCHK" -m "release_b5/recompute/comparator commit of the block-5 agree verdict"
git tag -a paper1/pre-unseal-$(date -u +%Y%m%d) <paper1 commit> -m "Paper 1 outcome text, written before the release event"
git push origin b5/release-check-r4 paper1/pre-unseal-$(date -u +%Y%m%d)
```

**A8. The post-release information rule.**
- Name the readers: the lead plus the A2(5) gate seat.
- Name the blind repair seats.
- Keep released values out of git until E and the gate close.
- Repair briefs and PR bodies carry structure only.
- Keep the reader log at `$BUNDLE/../READER-LOG.txt`, outside the repo.

**A9. Optional hardening.**
- Add `record_sha256` and the digests of `recompute.json` and `comparison.json` to the verdict.
- Drop the per-family counts from the public verdict on an agree.
- Promote `extract_blind.py` to `scripts/` with a test.
- Fix runbook line 66.

### B. Release check at r4 (unchanged; `RELEASE-RUNBOOK-lean.md` §1)

```sh
test -z "$(git status --porcelain --untracked-files=all)" || echo "checkout not clean"
nice -n 19 taskpolicy -b python3.13 -B scripts/release_b5.py --custody "$CUSTODY" --window-index "$INDEX" \
  --pinned-commit "$PINNED" --restricted-out "$REL" --workers 10; echo "exit=$?"
```

Exit 0 is required. Exits 1 and 2 follow the runbook §2 table.

### C. Release event (the unblinding boundary; record it before reading anything)

**C1. Verify, structure only:**

```sh
python3 -I - "$REL/verdict.json" "$PINNED" <<'PY'
import json,sys
v=json.load(open(sys.argv[1]))
assert v["verdict"]=="agree" and v["reason"] is None and v["pinned_commit"]==sys.argv[2]
assert all(f["verdict"]=="agree" for f in v["stages"]["comparator"]["families"].values())
print("release_checkout", v["release_checkout"]["commit"])
PY
```

**C2. Registration §12 manual rule.** For each analysed window, the inventory, registration and catalog digests recorded by the harvest must equal `SEAL_RECORD.md` §4 and the second-seal table. The files are `derived/code-identity.json`, `derived/harvest-thresholds.json` and `derived/window_flags.json`, all releasable. The harvest commit in `harvest.json` must equal the harvest addendum's pin.

**C3. Ed's OK.** Record the message id.

**C4. Collect the digests for the event:**

```sh
{ echo "record $(shasum -a 256 "$CUSTODY/dry-run/B5-BLIND-DRY-RUN-RECORD.json"|cut -d' ' -f1)"
  for f in verdict.json recompute.json comparison.json; do echo "$f $(shasum -a 256 "$REL/$f"|cut -d' ' -f1)"; done
  echo "bars $(git show "$RCHK":configs/analysis/b5/recompute_bars.json|shasum -a 256|cut -d' ' -f1)"
  echo "index $(shasum -a 256 "$INDEX"|cut -d' ' -f1)"
  git show "$PINNED":configs/analysis/b5/seal_pins.json | python3 -I -c 'import json,sys;[print(k,v) for k,v in sorted(json.load(sys.stdin)["sealed"].items())]'
  python3 -I -c 'import json,sys;r=json.load(open(sys.argv[1]));print("analysis",r["analysis_commit"],r["window_index_sha256"]);[print("window",w["pack"],w["plan_id"],w["harvest_record_sha256"]) for w in r["windows"]]' "$CUSTODY/dry-run/B5-BLIND-DRY-RUN-RECORD.json"
} > /private/tmp/b5-release-event-digests.txt
```

**C5. Append "Release event" to `SEAL_RECORD.md`.** Include:
- the UTC time and the writing seat;
- the signing statement "the lead has seen no Block 5 energy or outcome value before this entry";
- all C4 digests, the analysis tag and the release-check tag;
- the addendum's reference;
- DLE-0..n and D-188..190 by reference;
- the designated readers and Ed's OK id.

Commit on a branch, open a PR, merge. **Only then read.**

### D. Freeze the release bundle

```sh
BUNDLE="$(dirname "$CUSTODY")/b5-release-bundle-r4"
python3 -I - "$CUSTODY" "$REL" "$BUNDLE" <<'PY'
import hashlib,json,sys; from pathlib import Path
c,r,b=map(Path,sys.argv[1:]); rec=c/"dry-run/B5-BLIND-DRY-RUN-RECORD.json"; b.mkdir(mode=0o700); sums=set()
def put(src,name):
    d=src.read_bytes(); h=hashlib.sha256(d).hexdigest(); dst=b/name; dst.parent.mkdir(parents=True,exist_ok=True,mode=0o700); dst.write_bytes(d); sums.add(f"{h}  {name}"); return h
put(rec,"B5-BLIND-DRY-RUN-RECORD.json")
for row in json.loads(rec.read_bytes())["steps"]:
    for o in row["outputs"]:
        assert put(c/"dry-run/restricted"/o["name"],"outputs/"+o["name"])==o["sha256"], o["name"]
for n in ("verdict.json","recompute.json","comparison.json"): put(r/n,"release/"+n)
(b/"SHA256SUMS").write_text("\n".join(sorted(sums))+"\n")
PY
chmod -R a-w "$BUNDLE"; (cd "$BUNDLE" && shasum -a 256 -c SHA256SUMS | tail -1); shasum -a 256 "$BUNDLE/SHA256SUMS"
```

Put the `SHA256SUMS` digest in the release event, or in a dated addendum to it.

### E. Render, hand-check, gate (renderer and filler at tagged commits)

**E1.** Add the first-read entry to `READER-LOG.txt`: seat, UTC time, and the files opened.

**E2. (build, A5 interface)**

```sh
python3.13 -B scripts/render_b5_results.py --bundle "$BUNDLE" --seal-record docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md --prepare-checks "$CHECKS"
python3.13 -B scripts/render_b5_results.py --bundle "$BUNDLE" --checks "$CHECKS" --out "$RESULTS"
python3.13 -B scripts/render_b5_results.py --bundle "$BUNDLE" --checks "$CHECKS" --validate-rendered "$RESULTS"
```

**E3.** Hand-check every PENDING leaf against the A2(6) sources and record each in `$CHECKS`.

**E4.** The A2(5) gate seat re-runs `--validate-rendered`, samples leaves against `$BUNDLE`, and checks the paper against §2.4. The record stays out of git until F.

### F. Fill Paper 1

```sh
python3 -I docs/paper/paper1/fill_paper1.py --provenance "$RESULTS/provenance.json" --map docs/paper/paper1/fill_map.json \
  --draft docs/paper/paper1/paper1.md --out "$BUNDLE/../paper1.filled.md"          # (build)
rg -n '\{\{FILL:' "$BUNDLE/../paper1.filled.md"        # only adopted STOP_FILL ids may remain
python3 docs/paper/build/check_markdown.py "$BUNDLE/../paper1.filled.md"
python3 docs/paper/build/build_paper.py "$BUNDLE/../paper1.filled.md"
```

Fill the remaining ids from these sources:
- `P1-RELEASE` from the event;
- `P1-DEV-LIST` from the DEVIATION-LOG, D-188..190 and the seal-record errata and addenda;
- `P1-RECOMPUTE` from a **(build)** per-family summarizer over `$BUNDLE/release/comparison.json`, with the Block-5 bars.

### G. Bookkeeping, only after F and the gate close

- Update `CLAIMS_STATUS.md` and `PROJECT_STATUS.md`. RUN_STATE gets pointers only until repairs close.
- Run `python3 scripts/gen_state.py --check`.
- Close or supersede #648, #651 and #655, and #652 after the port.
- Update CANONICAL.
- Then FREEZE-BY-COMMIT-01, Ed's "trim first". Its phase-1 rehearsal must re-run E2 from the tags.
- Then the Block-6 release, which is gated on Block 5, with DLE-2's §17 entry still owed.
- Then Ed decides P1-AVAIL: which raw captures to make public.

**Any defect found after unseal** goes through plan §3.2 item 3:
- blind authors and reviewers;
- a synthetic fixture that reproduces it;
- every other fixture byte-identical;
- outputs labelled as produced after unblinding.

---

## 5. Effort, and what blocks the unseal

**Hard prerequisites before the release event:** A1, A2(1)-(6), A3 (the outcome-text parts), A4, A7 (the addendum), A8. These are mostly lead rulings plus about 2-4 h of writing, and can run in parallel with the r4 dry run (about 1 h 40 min).

**Strongly recommended:** A5 and A6, about 1 day with local Sol doing the code while I review. They make C to F mechanical.

**Can follow:** A9.

The 15 Nov results freeze leaves room for this.

---

## 6. What I checked by running

`release_b5.py` on an empty fake custody (exit 2, `dry_run_record_missing_or_incomplete`):
- stdout and `verdict.json` bytes differ (F7a);
- the folder is created with mode 0700 and the file inside with 0644;
- the verdict fields are as described in F7b.

Everything else in this report comes from reading code and documents at the commits named above.
~~~~
