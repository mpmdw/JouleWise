# ROW L11-retained-characterization-basis — Publication basis (NON-GATING)
Original verdict: NOT-READY (0 blockers / 3 should-fix / 2 nits / coverage 14/16)
Falsifiers 5 · unexecuted obligations 6 · ED-QUAL rows 0
Citation: `docs/process_traces/2026-08-15-readiness-council/sitting-packet-FINAL.md` §2 seat-verdict table (line 34); seat report `.../seat-reports/L11-retained-characterization-basis-report.md` (sha16 `484a6a0421fd421a`, packet §1).

**Seat scope, stated so it is not mis-aggregated.** L11 is the only non-gating seat. Cold ruling
seat table (line 29): "L11 Retained characterization basis (non-gating) | NOT-READY | Outside launch
aggregation; its three should-fixes are **paper-integrity defects** and enter the work-order program
on the paper lane." Its findings do not bear on launch GO; they bear on the P1 paper. The verdict's
own headline counts it anyway: "**NOT-READY. 0 READY / 11 NOT-READY** (ten gating seats **and the
non-gating L11 basis seat**)".

**Assembly note on the reading head.** The brief names `impl/r2-s0-mint-resolver` @ `d10881b`; the
worktree is actually at **`79a4cd0`** (two commits later; `d10881b` is its ancestor). `main` ==
`origin/main` == `0099382`. Read at `79a4cd0`.

**Headline for the seat:** unlike every other row in this packet, L11's three should-fixes were
**actually repaired, verified in the current paper text, and are merged to main.** The two nits were
not. One structural gap (the missing verdict artifact) was closed by *disclosure*, not by producing
the artifact.

---

## L11-SF1 — The ±31 ms / 33 W / ~1 J triple is presented as "the measured corpus figure"

### (a) Original finding (VERBATIM)
> - [should_fix] [L11] Paper presents the ±31 ms / 33 W / ~1 J triple as 'the measured corpus figure'; it is a single-member maximum plus a derived quotient

Citation: sitting-packet-FINAL.md §4 (packet line 169). Seat report §5:
> **SF1 (should-fix) — draft-v1.md:108, :112 (also :7, :240).** "The measured corpus figure is ±31 ms across ~33 W" / "at corpus precision" overstates provenance: ±31 ms is the single widest member's composed bound (corpus 25.6–31.1 ms), ~33 W is that member's envelope/bound quotient (corpus quotients 21–58 W; r01's measured mean-power step 18.6 W), ~1 J is the low end of the prefill-cell envelopes (0.98–1.47 J). Failure scenario: a metrology referee asks which artifact records 33 W; none does. Fix: state ranges, or pin the triple to its defining member and derivation.

Seat report §3 supporting derivation: "**Corpus-wide (30 members): 25.62–31.07 ms, mean 27.3 ms —
±31 ms is the maximum, held by exactly one member.**" / "No retained artifact records a 33 W step.
33 W = 1.016 J / 31.07 ms = 32.7 W — the envelope/bound quotient of that same single member."

No refuter verdict slot (should-fix tier; §9 refuters covered blockers only).
Post-verdict adjudication: routed into the Phase-1 should-fix batch — council-verdict.md
"**Phase 1 — parallel code WOs:** … should-fix batch incl. sweep verify-and-fix items … and **L11's
three paper corrections**."

### (b) What changed since 2026-08-15 — REPAIRED
- **Repair commit: `36c9d78` "Should-fix batch: sweep B1/B2/B3/B6/B7 + council L11 paper corrections"**
  (Ed R, 2026-08-15 22:22:44 −0700). Its message states: "L11 SF1-SF3: corpus triple pinned to member
  p2015-df-ph-prefill-abs-r01 (31.07 ms / 1.016 J / 32.7 W derived — lead bit-verified vs retained
  summary_metrics.json); a10-basis provenance fixed at all sites; whole-window PASSED prose now carries
  the re-derivation basis." Diff to `docs/paper/draft-v1.md`: 18 lines changed (9 +/9 −), touching the
  abstract, §3 body, the Figure 2 caption, §4 label paragraph, and §7.
  WHERE it lives: **merged to main** — `git merge-base --is-ancestor 36c9d78 main` → true.
- **Verified by reading the current text, not the commit message.** `docs/paper/draft-v1.md` is
  byte-identical between HEAD `79a4cd0` and `main` (later paper commits `2952226` plain-language pass
  and `53e480e` enrichment are branch-only, but their content reached main via the sync commits
  `3b4e3f8` and `ca6e2c7` — verified: `git diff --quiet main HEAD -- docs/paper/draft-v1.md` passes).
  Current text at the four SF1 sites:
  - **`:7` (abstract)** — "The characterization retained here supports no claim of its own. It comes
    from 30 runs in window a10 that repeat a single phase, with window a9 supplying reference and
    bracketing-calibration context: the combined bound on where a phase edge may fall spans
    **25.6–31.1 ms**, and the phase energy this leaves uncertain is on the order of a joule."
    The old sentence "an approximately ±31 ms boundary shift across an approximately 33 W power swing
    can mis-attribute about one joule" is **gone**.
  - **`:118` (§3 body)** — now gives the three ranges and then: "The familiar ±31 ms / ~33 W / ~1 J
    illustration comes from one particular run, `p2015-df-ph-prefill-abs-r01`: its 31.07 ms bound and
    1.016 J prompt-processing envelope give a quotient of 32.7 W." Also: "Dividing each run's
    phase-energy envelope … gives 21–58 W; **these are quotients we computed, not power steps anyone
    measured.**"
  - **`:122` (Figure 2 caption)** — "Schematic; **every value drawn in the figure is illustrative, not
    a measured corpus triple.**" The pre-repair caption read "(illustrative: 0.030 s x 33 W ~= 1 J;
    **the measured corpus figure is +/-31 ms across ~33 W**)" — that clause is deleted.
  - **`:258` (§7 limitation)** — "Across the 30 phase-repeatability runs of window a10, the combined
    bound on that placement spans 25.6–31.1 ms; each run's phase-energy envelope divided by its own
    bound gives 21–58 W; and the ordinary prompt-processing envelopes span 0.98–1.47 J. … Those watt
    figures are quotients we computed, not power steps anyone measured".
  - Also added at **`:252`** (§7 lead-in; the `36c9d78` original sat at `:233` and was reworded by the
    plain-language pass without loss): "The attribution-limited resolution item below **quotes the full
    range of what was retained, rather than presenting one run's largest bound and its derived quotient
    as though they described the whole corpus.**"
- **The repair survived two later paper passes.** `2952226` (plain-language pass, "numbers and claims
  frozen") and `53e480e` (current-state enrichment) rewrote the surrounding prose; the range wording,
  the member pin, and the "quotients we computed" disclaimer are all present in the current text.
  `0a216b7` and `c0ee784` also touched the paper without disturbing them.

### (c) Candidate disposition for the seat
**READY-EVIDENCE-ATTACHED.** The seat is adjudicating whether pinning the triple to
`p2015-df-ph-prefill-abs-r01` and stating the three corpus ranges fully discharges "state ranges, or
pin the triple to its defining member and derivation" — and whether one residual (`:149` still says
"the figure's **±30 ms** / 33 W / 1 J values remain illustrative", a fourth number not in the
corrected triple) is a leftover or a deliberate reference to what the figure draws.

### (d) Skeptical probes
1. `grep -n "corpus figure\|corpus precision" docs/paper/draft-v1.md` — the offending phrases should
   return zero hits. (Assembler: zero.)
2. `sed -n '149p' docs/paper/draft-v1.md` — "the figure's **±30 ms** / 33 W / 1 J values remain
   illustrative". Is ±30 ms what `figures/fig1_boundary_attribution.svg` actually draws? Open the SVG.
   If it draws ±31, the paper now carries a fourth inconsistent number.
3. The commit claims "lead bit-verified vs retained `summary_metrics.json`". Ask for the member's
   retained summary and recompute 1.016 / 0.03107 = 32.7 W yourself.
4. The seat report says r01's *measured* mean-power step is 18.6 W (45.6 → 27.0 W). The paper never
   states this. Should the honest correction include the measured step alongside the derived quotient?
5. `git log --oneline -- docs/paper/draft-v1.md` since `36c9d78` — five commits. Diff each against the
   corrected sentences to confirm no later pass silently reverted the provenance wording.

---

## L11-SF2 — The phase mis-attribution evidence is attributed to "the a9 and a10 windows"; a9 has zero phase members

### (a) Original finding (VERBATIM)
> - [should_fix] [L11] Paper attributes the phase mis-attribution evidence to 'the a9 and a10 windows'; a9 contains zero phase-absolute members

Citation: sitting-packet-FINAL.md §4 (packet line 170). Seat report §5:
> **SF2 (should-fix) — draft-v1.md:7, :108, :240.** The phase mis-attribution evidence is attributed to "the a9 and a10 windows"; a9 holds zero phase members. Failure scenario: reviewer requests a9 phase members; none exist (and a9's ±33.5 ms ref bounds would strain the ±31 ms headline if counted). Fix: a10's 30 phase-absolute members are the basis; a9 is reference/bracket context.

Seat report §4 falsifier F3: "corpus wording: hunted a9 for any phase-absolute member → none exist
(7 request-level refs, bounds 30.0–33.5 ms, + 12 refcorpus). (Outcome: finding SF2.)"

Post-verdict adjudication: same Phase-1 should-fix batch as SF1.

### (b) What changed since 2026-08-15 — REPAIRED
- Same repair commit **`36c9d78`**, **merged to main**. The pre-repair abstract read "The retained
  bracket-calibration corpus, **comprising the a9 and a10 windows**, provides the non-claim
  characterization"; the pre-repair §3 read "the retained bracket-calibration corpus—**the a9 and a10
  windows**—shows the same phenomenon at corpus precision"; the pre-repair §7 read "In the retained
  bracket-calibration corpus—**the a9 and a10 windows**—an approximately ±31 ms boundary shift…".
- **Current text, verified by reading, at all four sites (identical on HEAD and main):**
  - `:7` — "It comes from 30 runs in window a10 that repeat a single phase, **with window a9 supplying
    reference and bracketing-calibration context**".
  - `:118` — "**Window a9 supplies reference and bracketing-calibration context but contains no
    phase-repeatability runs.**"
  - `:149` (§4 publication-label paragraph, a site the seat did **not** cite — added by the repair) —
    "The retained characterization behind this label comes from the 30 phase-repeatability runs of
    window a10; **a9 contributes reference and bracketing-calibration context only**".
  - `:258` (§7) — "**Window a9 supplies reference and bracketing-calibration context but no phase runs.**"
- `grep -n "a9 and a10" docs/paper/draft-v1.md` at HEAD returns hits only where the phrase is
  *correct* (e.g. `:137`, "The original whole-window verdict files for a9 and a10 were not kept" —
  both windows genuinely had verdicts) and `:260` ("The retained a9 and a10 characterization quoted in
  Sections 3 and 7 … stays what it already was, diagnostic evidence about the instrument"), which is a
  claim-path statement, not a phase-evidence attribution. A seat should judge `:260` on its own terms.

### (c) Candidate disposition for the seat
**READY-EVIDENCE-ATTACHED.** The seat is adjudicating whether the a10-only basis is now stated at
every consuming site, including `:260`, which still names "the retained a9 and a10 characterization"
in the corpus-retirement paragraph.

### (d) Skeptical probes
1. `grep -n "a9" docs/paper/draft-v1.md` — read every hit and classify each as (correct context claim)
   vs (residual phase attribution). Assembler classified `:260` as ambiguous.
2. The seat found a9's reference bounds run to **33.5 ms**, wider than the ±31 ms headline. Does the
   paper anywhere let a reader infer a9 bounds are inside the stated 25.6–31.1 ms range?
3. Does the same correction need to land in `docs/instrument_guide*` / `README.md` / `CLAIMS_STATUS.md`?
   `36c9d78` touched only README + paper + queue + decision log + alpha_arm_readiness — check whether
   any other advisor-facing surface still says "a9 and a10 windows" for the phase evidence.
4. Confirm the count "30 phase-repeatability runs" against the retained a10 custody, not against the
   seat report.

---

## L11-SF3 — Whole-window PASSED verdicts for a9/a10 exist only as close-out prose; no verdict artifact is retained

### (a) Original finding (VERBATIM)
> - [should_fix] [L11] Whole-window PASSED verdicts for a9/a10 exist only as close-out prose; no verdict artifact is retained anywhere findable

Citation: sitting-packet-FINAL.md §4 (packet line 171). Seat report §5:
> **SF3 (should-fix) — custody CLOSE_OUT.md / retained extraction.** The a9/a10 whole-window PASSED verdicts are prose-only; the retained extraction itself refuses `whole_window_neg8_verdict_missing`, and no verdict artifact exists locally, in custody, in-repo, or in the iCloud mirror. Mitigation shown above: excursions re-derive exactly from retained refs. Fix: commit that re-derivation beside the close-out (or recover the original artifacts), or strip PASSED context from consuming docs.

Seat report §3: "**Whole-window PASSED (context).** No verdict artifact is retained anywhere findable
— but the excursions re-derive exactly from retained references: a10 max pairwise excursion among
start-mean/midpoint/end-mean = **0.5094 J in both families** (close-out: '0.509 J both families') vs
allowances 0.652/0.658 J; a9: 0.310/0.305 J vs 0.624/0.609 J. Both pass."

Triage WO-3 (`triage.json:717`) named the three options in priority order: "commit the excursion
re-derivation … beside the custody close-out, or recover the original verdict artifacts from wherever
they were emitted; alternatively strip PASSED context from consuming docs."

### (b) What changed since 2026-08-15 — REPAIRED BY DISCLOSURE (option 3), NOT BY ARTIFACT (options 1–2)
- Same repair commit **`36c9d78`**, **merged to main**. It inserted one new paragraph into §4, after
  the drift-allowance derivation. Current text at `docs/paper/draft-v1.md:137` (HEAD == main):
  > The original whole-window verdict files for a9 and a10 were not kept. The reference runs that were
  > kept do, however, re-derive the drift figures exactly: the largest excursion for a10 is 0.5094 J on
  > total energy and 0.5094 J on idle-subtracted energy, against allowances of 0.652 and 0.658 J; for
  > a9 the excursions are 0.310 and 0.305 J against allowances of 0.624 and 0.609 J. Any statement that
  > those drift screens passed therefore rests on this re-derivation rather than on a preserved verdict file.
  (The `36c9d78` original was denser prose; the current sentence is `2952226`'s plain-language rewrite,
  which preserved every number and the disclosure.)
- **NO verdict artifact was produced or recovered.** Repo-wide search at head `79a4cd0`:
  `grep -rn "0.5094" . --exclude-dir=.git` returns exactly four relevant hits — the paper line above,
  two council-trace files (`triage.json:717,746`, the L11 seat report `:47`), and one unrelated
  pre-existing value in `docs/process_traces/2026-07-24-diagnostic-extraction/diagnostic_details.json`.
  **No re-derivation artifact was committed beside any custody close-out**, and no recovered verdict
  file exists in the tree.
- **No decision-log record exists that the artifact cannot be produced.** Searched
  `docs/decision_log.md` for `0.5094`, `0.509 J`, "verdict artifact", "not retained", "were not kept"
  → **zero hits**. `36c9d78`'s decision-log diff is 18 added lines and is entirely the **D-130 closure**
  (sweep item B3), not an L11 record. The only place the non-existence is recorded is the paper itself.
- The refusal code the seat cited is real and unchanged: `whole_window_neg8_verdict_missing` appears in
  `tests/test_floor_extraction.py:1393`, `tests/test_mint_floor_artifact_generalized.py:8592`,
  `tests/test_analysis_integration.py:1941`, `tests/test_whole_window_selection.py:3058,3107`.
- **The one qualification row that would supply CLI-level PASSED evidence is still OPEN.** ED-L10-1
  ("one desk replay of the complete post-collection chain against a RETAINED real window corpus
  (a9/a10 custody, Ed-held off-repo) — whole-window verdict (expect passed), duration-margins recorder,
  backup, governed extraction …", sitting-packet-FINAL.md §5) is listed as still owed at
  `RUN_STATE.md:459` and `:546` and `docs/process/ed-batch-packet.md:57` ("a9/a10 desk replay").
  The 2026-08-17/18 Ed session closed D-127 sudoers, sampler lifecycle, rail probe, backlight rows,
  ED-QUAL-L4-1 and ED-Q-L9-3 (`docs/run_reports/2026-08-18-t10-session.md:102-110`) — **a9/a10 desk
  replay is not among them.** WHERE these records live: all merged to main.

### (c) Candidate disposition for the seat
**STILL-OPEN (partially repaired).** The consuming-doc half is discharged — the paper now states the
verdict files were not kept and that any PASSED statement rests on re-derivation. The artifact half is
not: no re-derivation was committed beside the custody close-out, no verdict was recovered, and no
decision records that it cannot be. The seat is adjudicating whether option 3 alone is sufficient for a
publication-basis row, given that the re-derivation now exists **only inside the paper's own prose** —
the same prose-only failure mode the finding named, moved one document over.

### (d) Skeptical probes
1. `grep -rn "0.5094" . --exclude-dir=.git` — is the paper still the only non-council home for the
   re-derivation? If someone claims custody now holds it, ask for the path and the digest.
2. Read the a9 and a10 `CLOSE_OUT.md` in `~/JouleWise-window-custody/` — was anything appended after
   2026-08-15? (Assembler could not verify custody-side files for this row.)
3. Is the re-derivation *reproducible* by a reader? The paper gives the six numbers but names no script,
   no member set, and no digest. Ask which command regenerates 0.5094 J.
4. `grep -n "D-054\|a9\|a10" docs/decision_log.md | tail -40` — should the non-existence of the verdict
   artifact be a registered limitation (the project registers limitations for less: see the
   TRUSTED-OPERATOR limitation from `65cc0f3`)?
5. ED-L10-1 would produce the CLI-level PASSED basis. Confirm it is still open in `RUN_STATE.md`
   §Ed-owed and ask whether the READY-candidate sitting should proceed with it outstanding — noting
   L11 is non-gating, so it does not block launch, only the paper claim.

---

## L11-N1 — a9 MANIFEST.sha256 lists ./backup.log

### (a) Original finding (VERBATIM)
> - [nit] [L11] a9 MANIFEST.sha256 lists ./backup.log, which is neither resident nor covered by PRUNED.md's enumeration

Citation: sitting-packet-FINAL.md §4 (packet line 172). Seat report §5:
> **N1 (nit) — a9 MANIFEST.sha256.** Lists `./backup.log`, neither resident nor covered by PRUNED.md's 28-plist enumeration (29 missing vs 28 authorized).

Triage failure scenario (`triage.json:752`): "A strict manifest verification reports 29 missing entries
where the prune note authorizes exactly 28 plists; the unexplained backup.log discrepancy costs an
auditor time or seeds doubt about the prune's completeness. All 173 resident files re-hash clean."
Triage WO-4 (`:718`): "(optional bookkeeping): annotate a9 MANIFEST/PRUNED for the backup.log entry and
correct the two D-054 prose figures (nits N1/N2)."

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** The artifact is Ed-held off-repo custody (a9 window bundle), so no repo commit
  could carry the fix. Searched the repo for any record of the annotation: `grep -rn "backup.log"
  docs/ TASK_QUEUE.md RUN_STATE.md` at head `79a4cd0` returns only (i) pre-existing backup-tooling
  references — `docs/risk_register.md:301`, `docs/stream_logs/2026-07-17-p2015-floors-prep.md:241,262`;
  (ii) the council's own records of the finding — `triage.json:750,752`, `sitting-packet-FINAL.md:172`,
  `seat-reports/L11-…:65`; and (iii) an unrelated L6 finding about `backup_runs.sh` writing an unhashed
  `backup.log` line (`seat-reports/L6-SEAM-READER-A-report.md:49`, `triage.json:53`).
  No annotation, no WO-4 row, no decision record. WHERE searched: all of `docs/`, TASK_QUEUE, RUN_STATE
  at HEAD (all merged to main for these files).
- Note for the seat: L6's separate finding explains *why* the entry exists — `backup_runs.sh` writes an
  unhashed one-line `backup.log`, which the manifest then lists. The two findings are the same artifact
  seen from two seats; neither was repaired.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND (nit, off-repo artifact).** The seat is adjudicating an off-repo bookkeeping
annotation that no work order tracks; the assembler cannot inspect the a9 MANIFEST from the read-only
worktree and searched the repo's record space instead.

### (d) Skeptical probes
1. Open the a9 custody `MANIFEST.sha256` and `PRUNED.md` directly and count: 29 missing vs 28
   authorized? Is `./backup.log` annotated now?
2. `grep -rn "WO-4\|N1/N2" docs/process/state_kernel.json TASK_QUEUE.md` — is the optional bookkeeping
   WO registered anywhere? (Assembler: no.)
3. Cross-check against L6's finding at `seat-reports/L6-SEAM-READER-A-report.md:49` — should these be
   one repair (`backup_runs.sh` hashing its own log) rather than two annotations?

---

## L11-N2 — Two D-054 decision-log prose details do not reproduce exactly

### (a) Original finding (VERBATIM)
> - [nit] [L11] Two D-054 decision-log prose details do not reproduce exactly from the retained bundles

Citation: sitting-packet-FINAL.md §4 (packet line 173). Seat report §5:
> **N2 (nit) — decision_log.md D-054 entry.** "Settled pair 3 h apart, 0.007 J" not uniquely reproducible; "fiducial 24.9 ms (80–87%)" is actually 80–97% across members. Neither is paper-cited.

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** Both prose details are unchanged at head `79a4cd0`:
  - `docs/decision_log.md:4689` — "…hours apart agreed to 0.007 J), but each member carries a"
  - `docs/decision_log.md:4693` — "measured — fiducial 24.9 ms (80-87%) plus bundle-local 3.3-6.1 ms"
  The seat's correction (80–97% across members) has not been applied.
  WHERE: `docs/decision_log.md` — verified at HEAD; the D-054 body is a 2026-07-25 entry long since on
  main and untouched by any post-council commit (`36c9d78`'s only decision-log change is the D-130
  closure block, verified by reading `git show 36c9d78 -- docs/decision_log.md`).
- The seat itself noted "Neither is paper-cited", so no publication surface carries the error.
  Corroborated: `grep -n "0.007 J\|80-87\|24.9 ms" docs/paper/draft-v1.md` → zero hits.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND (nit).** The seat is adjudicating whether an internally-inconsistent D-054 prose
figure that nothing cites is worth a decision-log amendment — noting that D-054 is a ratified live
entry and amending it is itself a governed act.

### (d) Skeptical probes
1. `sed -n '4680,4700p' docs/decision_log.md` — read the D-054 passage and confirm both figures.
2. Re-derive the fiducial fraction across the 30 a10 members: is it 80–97%, as the seat found?
3. Is amending a ratified decision-log body permitted, or must it be a superseding clause? Check the
   project's own convention (the verdict's disposition 1: "Future manifest changes are worded as
   SUPERSESSION, never re-pin").

---

## L11-COVERAGE — coverage 14/16 (tied-narrowest denominator, flagged for priority attack)

### (a) Original record (VERBATIM)
Packet §2 seat-verdict table row:
> | L11-retained-characterization-basis | non-gating | NOT_READY | 14/16 | 0 | 3 | 2 | 5 | 6 | 0 |

Packet §6 (unexecuted obligations — coverage adjudication input), all six L11 rows verbatim:
> - [L11] Full power-trace re-integration for the remaining 29 a10 phase members (1/30 done exactly; the other 29 envelopes were accepted from sha-bound summaries whose digests I verified against the custody extraction).
> - [L11] Code audit of the reducer-side envelope method implementation (common_trace_shift_plus_independent_edge_corners_v3) in joulewise/reduce.py — I re-derived its output numerically for one member but did not read the implementation.
> - [L11] Deep audit of joulewise/whole_window.py verdict machinery (surveyed for schema/semantics only; the verdict artifact itself is absent — finding SF3).
> - [L11] a9 custody operator logs (window-chain/calibration logs) read in detail; a10's were read.
> - [L11] campaign_log.jsonl deep audit and raw plist parsing for the reference members.
> - [L11] Byte-parity verification of the iCloud archive mirrors against local dirs (layout and existence checked only; a9 parity rests on the PRUNED.md-documented verification).

Cold ruling (line 75):
> Seats with the narrowest denominators (L9 at 14/16, L11 at 14/16) are flagged for priority coverage attack at the re-audit; no present re-run is ordered since their verdicts are already adverse.

Council verdict:
> **The work-order program is NOT CERTIFIED COMPLETE** … every seat's evidence universe was self-nominated, and the one denominator adversarially tested fell. Closing all listed work orders does not entitle READY; the READY-candidate re-audit must re-enumerate every universe independently and run the adversarial coverage attack as a standing packet element.

Citations: sitting-packet-FINAL.md §2 line 34, §6 lines 257-262; cold-fable-ruling.md line 75;
council-verdict.md "VERDICT" §. WHERE: **merged to main**.

### (b) What changed since 2026-08-15
- **No L11 coverage re-enumeration has been performed.** No `docs/process_traces/` directory exists for
  an L11 re-audit; the only post-council seat re-audit in the repo is WO-L2-REAUDIT
  (`docs/process_traces/2026-08-15-l2-reaudit/`, `0f886d3`).
- The cold ruling's deferral is conditioned on "their verdicts are already adverse". L11's three
  should-fixes are now repaired (above), so a seat may be asked to move this verdict — at which point
  the deferral's own condition lapses and the coverage attack becomes live. This is the sharpest
  procedural question in the row.
- Obligation 1 (29 of 30 a10 members accepted from sha-bound summaries rather than full power-trace
  re-integration) is the load-bearing gap under SF1's corrected ranges: the paper now publishes
  **25.6–31.1 ms**, **21–58 W**, and **0.98–1.47 J** as corpus ranges, and 29/30 of those envelopes were
  never re-integrated from raw traces by this seat. Nothing since 2026-08-15 closes that.
- ED-L10-1 (a9/a10 desk replay) would touch obligations 3 and 5; it is still open (see SF3(b)).

### (c) Candidate disposition for the seat
**STILL-OPEN.** The seat is adjudicating a self-nominated 16-item universe that the cold adjudicator
singled out for priority attack, on a row whose findings are now repaired — i.e. exactly the situation
in which the deferral rationale ("verdicts are already adverse") no longer applies.

### (d) Skeptical probes
1. The paper's three published ranges rest on 29 envelopes this seat accepted from summaries, not
   traces. Who re-integrated them? Name the artifact, or accept the range as summary-derived.
2. `ls docs/process_traces/` for any L11 re-audit; compare with the L2 precedent.
3. Run the standing adversarial coverage attack: what publication-basis surface is in neither the 14
   nor the 6? (Candidates the assembler noticed: the instrument guide and `CLAIMS_STATUS.md`, which
   also consume the retained characterization but appear in no L11 universe item.)
4. Obligation 6 — a9's iCloud byte-parity "rests on the PRUNED.md-documented verification", and N1 says
   PRUNED.md's enumeration is itself off by one. Does N1 undermine obligation 6's mitigation?
5. Ask whether repairing three should-fixes without re-enumerating the universe is precisely the
   "closing all listed work orders does not entitle READY" pattern the verdict warned about.

---

## ROW-LEVEL OPEN ITEMS
- **The queue's claim was VERIFIED TRUE, but the queue is not the evidence.** `TASK_QUEUE.md:246`
  (CONDITIONAL-INSERT-TIGHTER-FLOOR) says "The council-ordered L11 provenance corrections to
  characterization prose are separately authorized and already applied." Independently confirmed by
  reading `docs/paper/draft-v1.md` at HEAD (identical to main) at `:7`, `:118`, `:122`, `:137`, `:149`,
  `:252`, `:258`, and by reading the `36c9d78` diff. `grep -c "corpus figure\|corpus precision"` → **0**. Repair commit `36c9d78` **is an ancestor of main**.
- **RUN_STATE contradicts this and is stale on main.** `RUN_STATE.md:522` still lists "L11's three paper
  corrections" inside "**4. Remaining Phase-1 launches:** … should-fix batch", four days after
  `36c9d78` landed them. A seat reading RUN_STATE alone would conclude the opposite of the truth.
  Same file, same list, also still says WO-CENSUS-SEMANTICS "needs Ed" after ED-Q-L9-3 was captured.
- **SF3 is only half-repaired.** The disclosure landed in the paper; the artifact did not. No
  re-derivation is committed beside any custody close-out, no verdict file was recovered, and
  **no decision-log entry records that the a9/a10 whole-window verdict artifacts cannot be produced** —
  searched `docs/decision_log.md` for `0.5094`, `0.509 J`, "verdict artifact", "not retained", "were not
  kept": zero hits. The re-derivation's only home outside the council trace is the paper's own prose.
- **The re-derivation is not independently reproducible from what is published**: `draft-v1.md:137`
  gives six numbers with no script, member set, or digest.
- **ED-L10-1 (a9/a10 desk replay) is still OPEN** — the one row that would supply CLI-level PASSED
  evidence. Owed per `RUN_STATE.md:459,546` and `docs/process/ed-batch-packet.md:57`; not among the
  rows the 2026-08-17/18 Ed session closed (`docs/run_reports/2026-08-18-t10-session.md:102-110`).
- **Both nits are unrepaired.** N1 (a9 `MANIFEST.sha256` listing `./backup.log`) is an off-repo custody
  artifact with no tracking row anywhere; N2's two D-054 prose figures still read "0.007 J" and
  "24.9 ms (80-87%)" at `docs/decision_log.md:4689,4693`. Triage's WO-4 exists in no queue or kernel.
- **A possible fourth number was introduced by the repair**: `draft-v1.md:149` says "the figure's
  **±30 ms** / 33 W / 1 J values remain illustrative" while `:118` names the ±31 ms / ~33 W / ~1 J
  illustration. Assembler did not open `figures/fig1_boundary_attribution.svg` to determine which the
  figure draws.
- **`draft-v1.md:260` still says "The retained a9 and a10 characterization quoted in Sections 3 and 7"**
  — correct as a claim-path statement, but it is the one surviving site pairing a9 with the §3/§7 phase
  content SF2 said belongs to a10 alone. Flagged, not graded.
- **No L11 coverage re-enumeration exists**, and the cold ruling's reason for deferring it ("verdicts
  are already adverse") is weakened now that the three should-fixes are repaired.
- **Assembler could not verify, from the read-only worktree**: the a9 custody `MANIFEST.sha256` /
  `PRUNED.md` contents (N1), whether anything was appended to the a9/a10 `CLOSE_OUT.md` after
  2026-08-15 (SF3 option 1), and what `figures/fig1_boundary_attribution.svg` actually draws.
- **Branch-vs-main note for the whole row**: `docs/paper/draft-v1.md`, `TASK_QUEUE.md` line 246's
  content, `RUN_STATE.md`, `docs/decision_log.md`, and `docs/run_reports/2026-08-18-t10-session.md` were
  all checked; `draft-v1.md` is byte-identical between HEAD `79a4cd0` and `main` `0099382`. The paper
  commits `2952226` and `53e480e` are branch-only but their content reached main via `3b4e3f8` and
  `ca6e2c7`; `6f4b553` and `0a216b7` and `c0ee784` and `36c9d78` are all on main.
