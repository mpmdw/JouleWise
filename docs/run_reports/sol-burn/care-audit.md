# Independent CARE audit: Block 5 analysis pipeline

**Audit date:** 2026-11-06. **Scope:** repository code and records only. No
experiment-data path was opened. This is a process audit, not a proposal to
change the released analysis.

## Bottom line

The advisor's description is fair: this pipeline treats a small energy study
like a custody-sensitive release system. Most of that care protects a real
property, but not every layer deserves its current price. The measured dry-j
run was about **153 min** at seven workers; the step ledger assigns 15 min to
initial validation, 27.5 min to brackets, 14 min to extraction, 23.5 min to
minting, and 65.5 min to steps 8--11. These are overlapping homes for several
guards, not additive guard-only costs (`docs/process/b5_speed_plan.md:20-49`).
Consequently this audit reports a standalone cost only where the repository
actually measured one; “embedded/unisolated” is not a claim of zero cost.

**Recommendation:** keep the scientific and blinding invariants; lighten
duplicate executions, not independent authentication; drop no preregistered
estimator or decision check. The clearest “nothing” layer is ceremonial
full-size synthetic duplication already made optional. The highest-value
future cuts (L4 cache eligibility and candidate-refit memoization) require a
ruling and the draft deviation entries below.

## CARE inventory

Protection labels below use the requested vocabulary. “Integrity” includes
provenance/custody; “safety” means fail-closed host/tool behavior, not subject
safety.

| # | Guard or ceremony | What it protects | Requiring rule / implementation evidence | Measured wall-time cost | Verdict |
|---:|---|---|---|---:|---|
| 1 | **Per-read authentication (L1/L2/L3 and v2 read sessions).** A consumer reads, hashes, strict-parses and registers the bytes it itself consumed; another program's successful result is not authority. | Integrity; reproducibility | D-188 permits content-hash independence only for programs that independently re-authenticate (`docs/decision_log.md:12243-12246`). The speed plan explicitly preserves independent authentication and exact cache keys (`docs/process/b5_speed_plan.md:161-169`). | Not isolated. Step 1 is **15 min**, step 4 **14 min**, and step 5 **23.5 min**, all dominated partly by authentication/reduction (`docs/process/b5_speed_plan.md:31,35-36`). | **KEEP**, but coalesce repeated reads inside one authenticated session where identity, grammar verdict, and serial replay remain exact. |
| 2 | **Strict JSON/JSONL grammar on every authenticated ingest.** UTF-8/JSON grammar, duplicate keys, non-finite numbers, malformed/blank JSONL records and vocabulary constraints fail closed. Success-only grammar memoization still binds the exact digest and stack-headroom premise. | Integrity; reproducibility | `authentication_io` defines JSONL as an authentication grammar and duplicate-key/strict parsers (`joulewise/authentication_io.py:44,600-606,674-753`); D-189 distinguishes malformed/duplicate/non-finite verdict bytes from legitimate scientific non-issuance (`docs/decision_log.md:12255-12258`). | Embedded. Step 1's 15 min includes strict plist/JSON validation; step 5's driver-serial authenticated I/O was estimated at about **560 of 1,205 synthetic seconds**, including strict parse and path resolution (`docs/run_reports/2026-11-06-b5-under-90.md:95-100`). | **KEEP** strictness; **LIGHTEN** only by shipping the already-successful digest-keyed grammar memo after a ruling, never by permissive parsing. |
| 3 | **Archive manifests and ordered source census.** Index authenticates `harvest.json`; `sources/SHA256SUMS` authenticates sources; regular-file/no-follow/size checks and reauthentication surround selection; first failure remains manifest-ordered. | Integrity; reproducibility | Archive code makes the index—not the archive—the harvest authority and independently authenticates structural outputs (`joulewise/b5_analysis/archive.py:217-280`); it re-reads a changed source manifest and bulk-hashes in manifest order (`joulewise/b5_analysis/archive.py:376-404,484-518`). | Step 0 was **4.642 → 3.870 s** for the three-window synthetic joined path while preserving digests; the production dry-j allocation is **2 min** (`docs/run_reports/2026-11-05-b5-speed-plan.md:49-56`; `docs/process/b5_speed_plan.md:30`). | **KEEP** the manifest and ordered comparison; the existing bulk census is the right lightening. |
| 4 | **Transfer/custody manifests.** Every transferred file has relative path, size and SHA-256; tar digest and total uncompressed size are recorded; unpacking verifies all files and requires a 25 GiB margin. | Integrity; safety; reproducibility | The transfer contract requires per-file manifests and tar hashes (`docs/process_traces/2026-10-27-l9-restart/BLOCK5-TRANSFER.md:38-48`) and verify-before-unpack/analysis (`docs/process_traces/2026-10-27-l9-restart/BLOCK5-TRANSFER.md:51-58`). | Not timed separately; one-time packaging/transfer, outside the 153-min analysis step ledger. | **KEEP** for cross-machine transfer. Do not repeat it for bytes that never cross a custody boundary. |
| 5 | **Hash independence, not trust propagation.** Content hashes may replace full re-reduction only after the receiving program independently authenticates the exact bytes. | Preregistered-estimator fidelity; integrity | D-188 item 2 authorizes this narrow substitution (`docs/decision_log.md:12244-12246`); the engineering rule says a hash is not permission to trust another program's result (`docs/process/b5_speed_plan.md:161-166`). | Avoided work is not yet isolated. The prospective target is part of step 5's proposed **5.5 min** saving, not demonstrated as an independent gain (`docs/process/b5_speed_plan.md:138-146`). | **KEEP** the independence boundary; **LIGHTEN** repeated arithmetic only when the authenticated referent and complete key are proven. |
| 6 | **VDL verified-derivation layer.** Run-scoped, content-addressed L1 strict-validation, L2 operative-summary and L3 reduction leaves; exact keys include scalar/tree/session/physics context. Hits replay auth rows/effects at the serial position. | Reproducibility; preregistered-estimator fidelity; integrity | VDL's contract is content-addressed and records tree/path/read effects (`joulewise/analysis_verified_store.py:1-71`); the speed-plan rule fixes exact key and replay behavior (`docs/process/b5_speed_plan.md:161-169`). | Benefit rather than pure cost; instrumentation/serialization was not isolated. VDL participates throughout the **153-min** run. | **KEEP**. It is the main principled substitute for repeated derivation. Simplify implementation only with shadow/equivalence coverage intact. |
| 7 | **Cache eligibility recorder and poison discipline.** A fill is storable only with observable reads, no unrecorded mutation/write/clock/thread effect, no deadline firing, eligible path semantics and an agreeing value. Failures are never cached; conflicting fills poison rather than overwrite. | Preregistered-estimator fidelity; reproducibility; integrity | The VDL records unstorable side effects and path-free restrictions (`joulewise/analysis_verified_store.py:53-71,141`); disagreements poison (`joulewise/analysis_verified_store.py:2480-2518`); the driver shares only verified physics fits and never caches failed fits (`joulewise/b5_analysis/dry_run.py:2001-2014`). | Recorder overhead not isolated. Current ineligibility causes substantial recomputation: making L4 storable is estimated to save about **12 min** (roughly 380 s in step 4 and 370 s in step 5), but this is a projection, not a measurement (`docs/run_reports/2026-11-06-b5-under-90.md:178-183`). | **LIGHTEN**, by narrowly making the read-only custody probe recordable/storable after a ruling. Do not relax poison, failure, deadline, or mutation rules. |
| 8 | **120 s calibration-refit deadline is a tooling refusal, never a usable fit.** Any firing, including in a worker, fails the step; the fresh run uses a new custody root. | Safety; integrity; blinding | Ed chose option (c): retain the frozen deadline and cure a firing blind in fresh custody (`docs/process_traces/2026-10-27-l9-restart/ED-RULING.md:55-67`). Driver code replaces the step result with the deadline/observer refusal (`joulewise/b5_analysis/dry_run.py:2055-2078`). | Normal-path overhead is observer bookkeeping; a firing costs the **entire attempt**. One idle VM fit was **10.29 s** against 120 s (`docs/process_traces/2026-10-27-l9-restart/ED-RULING.md:68-76`). | **KEEP** as a host-safety tripwire for Block 5. Do not “optimize” by accepting a timed-out fit. A later block may preregister a deterministic-only budget prospectively. |
| 9 | **Serial public phases and ordered consumption.** Steps remain `0→1→2→3→3b→4→5→8→6→9→9b→10→11`; parallel children are consumed alpha/beta/gamma and member order, so first refusal and floating-point accumulation stay fixed. | Preregistered-estimator fidelity; blinding; reproducibility | The speed plan fixes this order and forbids cross-step publication (`docs/process/b5_speed_plan.md:54-75`); D-188 requires identical refusal identity and position (`docs/decision_log.md:12243-12246`). | Large but mostly real dependencies. Construction-only pack serialization was reduced: step 3b **180.781 → 89.707 s**, step 10 cold **433.000 → 205.929 s**, step 11 **2752.383 → 2607.381 s**, step 5 **1467.026 → 1348.711 s** on synthetic S10 (`docs/process/b5_speed_plan.md:225-236`). | **KEEP** public phase and consumption order; **LIGHTEN** construction-only serialization with isolated workers and ordered commit. |
| 10 | **Frozen-file and pin rules.** Estimator sources, seal inputs, analysis tag, pack trees, flag/exclusion policy and calibration acceptance are bound; a bug needs a ruling/rebind rather than an invisible edit. | Preregistered-estimator fidelity; integrity; reproducibility | The registration defines one frozen head and hash-pinned packs (`configs/campaigns/v5_claim_25g83/registration_block5.md:158-200,743-778`); the deadline ruling rejected edits to governed estimator pins without reissue (`docs/process_traces/2026-10-27-l9-restart/ED-RULING.md:55-64`). D-190 demonstrates the permitted exception: fix, equal reference hunk, new tag, comparator (`docs/decision_log.md:12265-12272`). | Git/hash checks are seconds; the ceremony can cost a review/reissue cycle. No standalone wall timing is recorded. | **KEEP** the scientific freeze; **LIGHTEN** the social reading “frozen means never fix.” Use a dated ruling, rebind and blinded equivalence. |
| 11 | **Blinded comparator from an independent clone.** It imports no JouleWise code, owns its tier/exemption configuration, verifies referents, reports only MATCH/DIFFER field names in blinded mode, and writes valued detail only to restricted custody. | Blinding; preregistered-estimator fidelity; reproducibility | D-188 requires exact registered numbers and decisions and digit-free real-data comparison (`docs/decision_log.md:12243-12248`). Comparator independence and blinded grammar are explicit (`tools/b5_equivalence/compare_b5_results.py:1-17,48-54`). | Full comparator time is not separately recorded. It is a post-run gate, not included as a step in the **153 min** analysis ledger. | **KEEP**. This is what makes performance refactoring scientifically defensible. |
| 12 | **Independent recompute/release equality.** Release re-runs from authenticated inputs and refuses if the dry-run digest/input binding differs; the dry run and release are separate custody events. | Reproducibility; integrity; blinding | The release driver compares prior record, commit and window index and refuses a difference (`joulewise/b5_analysis/dry_run.py:2022-2053`). Ed retained the real release digest comparison while making duplicate full-size synthetic equality optional (`docs/process_traces/2026-10-27-l9-restart/ED-RULING.md:20-35`). | Roughly another complete production analysis when release mode reruns. Historical full-size synthetic release equality took **47,231.364 s (13.12 h)** on a 5-vCPU VM (`docs/process_traces/2026-10-27-l9-restart/ED-RULING.md:91-99`). | **KEEP** real dry-run/release equality. **DROP** mandatory full-size synthetic duplication; it is already optional. |
| 13 | **Fresh custody root after tooling refusal; immutable outputs/create-once boundaries.** A failed attempt is not repaired in place, so partial derived state cannot become a release. | Blinding; integrity; reproducibility | The blind dry run is cured blind and restarted in fresh custody (`docs/process_traces/2026-10-27-l9-restart/ED-RULING.md:14-20,64-67`); the driver creates a new restricted directory and stops subsequent ordinary steps after a refusal (`joulewise/b5_analysis/dry_run.py:1989-1997,2045-2087`). | Worst case: all elapsed time before the refusal. Normal successful-path cost is filesystem setup only. | **KEEP**. Cheap on success, decisive against state contamination. |
| 14 | **Run-wide verified physics cache, success only.** Identical calibration bytes are fitted once per run by content hash; failures and deadline-tainted fits never enter the cache. | Reproducibility; safety | Ed's amendment authorized one shared cache with byte-identical cached/uncached outputs (`docs/process_traces/2026-10-27-l9-restart/ED-RULING.md:36-50`); driver wiring states the success-only rule (`joulewise/b5_analysis/dry_run.py:1998-2014`). | The original joined fixture spent **63%** of wall time on 82 refits of one calibration; this guard is a major saving, not overhead (`docs/process_traces/2026-10-27-l9-restart/ED-RULING.md:36-45`). | **KEEP**. Extend only through complete content/context keys and the deviation process below. |
| 15 | **Tripwires: re-reduction, context, removed-reference and stored-summary equality.** Cached/parallel results do not bypass calibration-dependent summary comparison or kept-unit/source replay. | Preregistered-estimator fidelity; integrity | The deadline condition originally failed because reduce exited successfully with four changed fields; the added tripwire now refuses at step 2 (`docs/process_traces/2026-10-27-l9-restart/ED-RULING.md:68-74`). The speed plan expressly retains tripwires and stored-summary comparison (`docs/process/b5_speed_plan.md:32-33`). | Steps 2+3 total about **0.5 min** in the dry-j allocation (`docs/process/b5_speed_plan.md:32-33`). | **KEEP**. This is unusually favorable cost/risk. |
| 16 | **Primary-bound sensitivity equality, wider-bound pass, disclosures and fill replay.** Sensitivity cannot silently alter bound-independent values; null registered outcomes remain null; writers see only validated shapes. | Preregistered-estimator fidelity; reproducibility; blinding | D-190 fixes null behavior and demands identical outputs for all previously passing inputs (`docs/decision_log.md:12263-12272`). The speed plan forbids removing the primary-bound check and keeps bound/pass/consumer order (`docs/process/b5_speed_plan.md:44-49,115-119`). | Step 11 is **29 min** dry-j; synthetic pack parallelism saved only **145.002 s (5.3%)** (`docs/process/b5_speed_plan.md:44,232-239`). | **KEEP** the checks; **LIGHTEN** by running independent primary/wider computation concurrently only if consumption and comparison order remain fixed. |
| 17 | **Multiple independent/cold reviews and full-size synthetic rehearsals.** Review seats probe/mutate; historically, J1-J6/C5-C9 and full-size synthetic double runs preceded real analysis. | Safety; reproducibility; sometimes nothing (duplicated assurance) | Ed consolidated review into two simultaneous executing reviews and made full-size synthetic modules optional (`docs/process_traces/2026-10-27-l9-restart/ED-RULING.md:20-35,77-89`). | Historical full-size modules were about **6.16 h** and **13.12 h** on the 5-vCPU VM (`docs/process_traces/2026-10-27-l9-restart/ED-RULING.md:91-99`). Review time is human/agent wall time, not analysis runtime. | **KEEP** two bounded executing reviews for comparator/cache/freeze changes. **DROP** ritual full-size synthetic repeats once reduced branch coverage plus the real blinded gate exists. |
| 18 | **Structural-only handling of step-9b non-issuance.** It emits one indistinguishable outcome class, no sidecar/custody, and still runs steps 10/11; malformed/provenance-defective bytes remain tooling refusals. | Blinding; preregistered-estimator fidelity | D-189 defines the one code/shape and opaque-number parsing (`docs/decision_log.md:12255-12258`) and requires the comparator to treat absence/presence as a decision without values (`docs/decision_log.md:12259-12260`). | Negligible direct cost; prevents data-dependent stopping/status leakage. | **KEEP**. This is blinding logic, not ceremony. |

## What may be lightened without changing the estimator

1. Preserve every public serial boundary, but precompute independent pack work
   and consume it in registered order. This already produced exact synthetic
   commitments for steps 3b, 5, 10 and 11.
2. Ship only each worker's relevant VDL roots plus path-free entries rather
   than the entire store; preserve poison/defect propagation and consumed-only
   merge.
3. Authenticate a byte sequence once per read session, then reuse the
   digest-keyed strict-grammar verdict at an equal-or-safer stack headroom.
4. Make the read-only custody probe recordable so L4 can become storable, but
   only after a ruling and shadow comparison. Do **not** broadly whitelist
   threads or filesystem calls.
5. Prefetch candidate refits under the same 120 s observer and success-only
   cache. Serially consume the chosen candidate and discard all unconsumed
   entries/effects.
6. Keep real dry-run/release equality and the blinded comparator; do not pay
   again for mandatory 6 h/13 h full-size synthetic ceremonies.

## Draft deviation-log entries for preregistration-touching cuts

These are drafts, **not authority and not applied changes**. Each must be dated,
approved before use, pinned to a commit, tested on synthetic inputs, and pass
the blinded D-188 comparator on the real Block-5 tree before promotion.

### DEV-B5-CARE-01 — make the L4 bracket derivation storable

- **Proposed deviation:** Treat the named custody-probe thread's read-only
  `exists`/`is_dir` observations as recorded dependencies rather than an
  automatic VDL-unstorable condition. No other thread or operation is exempt.
- **Touches:** cache eligibility and therefore execution count, but not the
  bracket formula, selection, source census, refusal order or value.
- **Reason:** projected saving about 12 min across steps 4/5; current guard
  repeats an already verified bracket because of observation mechanics.
- **Required proof:** cold/hit/shadow equality; mutation between probe and
  consume refuses; missing/symlink/non-directory cases preserve first refusal;
  no hit after deadline firing; poison disagreement stops serving; comparator
  EQUIVALENT for P/D/R/I tiers.
- **Rollback:** `JOULEWISE_B5_VDL=off` or leaf ineligible; fresh custody rerun.

### DEV-B5-CARE-02 — run-scoped candidate-refit memo and parallel prefetch

- **Proposed deviation:** Memoize
  `_load_calibration_candidate_unbounded` by complete authenticated calibration
  content and governed context, and prefetch independent candidates. Keep
  `powermetrics_fiducial.py`, `reduce.py`, cell budget, 120 s wall observer and
  selected-candidate arithmetic unchanged.
- **Touches:** a frozen calibration-loading file/execution schedule and number
  of refits, not the estimator result.
- **Reason:** estimated 300--450 s saving in step 3b, potentially more where
  brackets are replayed.
- **Required proof:** every candidate independently authenticated; only the
  serially consumed result merges auth rows, poison and cache entries; failures
  and deadline firings never memoize; serial/prefetch first-refusal matrices;
  exact comparator equality.
- **Rollback:** disable prefetch/memo and rerun from fresh custody.

### DEV-B5-CARE-03 — ship strict-grammar success memo from workers

- **Proposed deviation:** Add L7 grammar verdicts to the existing worker memo
  payload only for exact digest/grammar/vocabulary identities and sufficient
  recorded stack headroom. Never ship failures.
- **Touches:** authentication execution count, not accepted grammar.
- **Reason:** projected saving up to about 120 s in synthetic step 5 and likely
  later replay steps.
- **Required proof:** duplicate keys, non-finite JSON, malformed/blank JSONL,
  encoding and deep-recursion cases produce the same refusal and position;
  unconsumed workers contribute no memo; exact comparator equality.
- **Rollback:** omit L7 from `SHIPPED_MEMOS`; fresh custody rerun.

### DEV-B5-CARE-04 — concurrent primary/wider sensitivity computation

- **Proposed deviation:** Compute the primary-bound equality pass and wider
  pass concurrently, but commit/compare primary first and preserve pack,
  contrast, disclosure and fill order.
- **Touches:** execution schedule of a preregistered sensitivity check, not its
  formula or decision.
- **Reason:** unmeasured prospective 300--600 s saving in the longest step.
- **Required proof:** null/non-issuable D-189/D-190 shapes, first-failing pack,
  changed-bound-independent-value tripwire, deadline/unconsumed merge rules,
  exact outputs and D-188 equality.
- **Rollback:** serial bound passes; fresh custody rerun.

No deviation entry is needed to stop requiring full-size synthetic duplicates:
Ed already made them optional while retaining the real blind dry run and
release gate (`docs/process_traces/2026-10-27-l9-restart/ED-RULING.md:20-35`).

## Estimator choices that must never change after unsealing

“Never” here means **not within this sealed analysis**. A later prospective
registration may choose differently. A defect can be fixed only through a
dated ruling/rebind plus blinded equivalence; it must not be disguised as a
performance optimization.

1. **Membership and exclusions:** analysed attempt selection, claim-usable
   status, registered flag effects, kept repeat/quad units, minimum counts,
   and the rule that the exclusion function never reads energy
   (`configs/campaigns/v5_claim_25g83/registration_block5.md:1381-1410`).
2. **Reported-cell point estimator:** stratified weight **0.2 repeats + 0.8
   quad members**, with its registered variance, degrees of freedom, t
   quantile, interval construction, J/token denominator and phase definitions
   (`configs/campaigns/v5_claim_25g83/registration_block5.md:905-923`).
3. **Timing/attribution bound:** the registered four-corner anchor-shift
   envelope; composition of fiducial, span and member clock bounds; maximum
   per-member attribution floor; and how the stratified average enters the
   reported interval (`configs/campaigns/v5_claim_25g83/registration_block5.md:814-943`).
4. **Detection-floor estimator:** null-quad construction, point and
   corner-widened floors, minimum kept units, aggregation across the registered
   floor cells, resolution status and mint provenance. The floor remains the
   largest registered null difference, not an empirically retuned threshold
   (`configs/campaigns/v5_claim_25g83/registration_block5.md:812-817`).
5. **Dominance ratio:** corner-widened floor divided by point floor, including
   zero-denominator/refusal behavior and the fixed `R ≥ 2` disclosure threshold
   (`configs/campaigns/v5_claim_25g83/registration_block5.md:1625-1639`).
6. **GAMMA contrasts:** the two prospective phases, quad difference
   `d=(B1+B2)/2-(A1+A2)/2`, mean over complete quads, registered direction,
   ratio/per-token forms and leave-one-quad stability check
   (`configs/campaigns/v5_claim_25g83/registration_block5.md:782-810,1635-1639`).
7. **Multiplicity and claim gate:** Holm family of two at familywise 5%, exact
   confirmatory manifest membership, interval-excludes-zero/direction/floor
   conditions, and no post-unseal swapping of primary and diagnostic claims
   (`configs/campaigns/v5_claim_25g83/registration_block5.md:1613-1639`).
8. **Calibration/bracket estimator:** acceptance artifact, ledger snapshot,
   pre/post bracket, drift allowance `max(observed_drift, bracket_screen)`,
   terminal ledger pin and candidate/refit arithmetic
   (`configs/campaigns/v5_claim_25g83/registration_block5.md:947-971`).
9. **NEG-8 reference drift estimator:** surviving-reference selection,
   endpoint/interior rules, realized-count t bound, gross and idle-subtracted
   screens, and pack-specific consequence of midpoint loss
   (`configs/campaigns/v5_claim_25g83/registration_block5.md:972-1036,1188-1195`).
10. **Sensitivity semantics:** primary-bound equality, wider-bound context,
    null propagation for exactly the registered non-resolvable/not-estimable
    states, disclosure text state and fill behavior (`docs/decision_log.md:12263-12272`).
11. **Decision/refusal semantics:** which outcome is scientific versus tooling,
    first-refusal identity and position, step-9b's sole non-stopping outcome,
    and the absence of fabricated sidecars/values (`docs/decision_log.md:12255-12260`).
12. **Equality standard:** every registered number exactly equal (not within a
    tolerance), every admit/refuse/select decision and refusal position equal;
    audit-only artifacts may differ (`docs/decision_log.md:12243-12246`).

## Audit disposition

The pipeline is over-ceremonial mainly where it duplicates *execution*:
full-size synthetic reruns and repeated authenticated reductions. It is not
over-careful in strict parsing, immutable custody, the independent blinded
comparator, fixed estimator/decision semantics, or refusing deadline-tainted
fits. The responsible simplification is therefore **fewer derivations with
stronger verified reuse**, not fewer validations or looser estimators.

This report changes documentation only. There is no analysis-code or
configuration diff, so successful-path analysis outputs are byte-identical by
construction.
