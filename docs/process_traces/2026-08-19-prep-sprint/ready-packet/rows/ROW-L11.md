# ROW L11 — RETAINED CHARACTERIZATION BASIS (charter tier: high, publication-basis; state **NON-GATING**)

> **Assembler note on the read tree.** The task named the read-only worktree at
> `impl/r2-s0-mint-resolver` @ `4597ad4`. The tree as found is at **`b92b43d`** (direct child of
> `4597ad4`). All findings below were read at `b92b43d`. `main` == `origin/main` == `0099382`.
> Every pointer is labelled **ON-MAIN** or **BRANCH-ONLY**.
>
> **This row assembles evidence. It does not grade the seat.**

---

## 0. Seat identity and 2026-08-15 result

- **Seat:** `L11-retained-characterization-basis` — charter §The fleet item 11, verbatim
  (`docs/process/instrument-readiness-audit-charter.md:55-57`):
  > 11. (NON-GATING) RETAINED CHARACTERIZATION BASIS (high): a9/a10 as the
  >    publication-basis audit, outside the launch-GO aggregation
  >    (amendment 13).

  The section heading itself reads "## The fleet (amendments 3-9; **ten launch-gating seats + one
  non-gating**)" (`:27`).
- **Seat question (seat report line 6):** "is the characterization the paper leans on — the ±31 ms
  / ~33 W / ~1 J attribution-limit chain — exactly what the retained a9/a10 artifacts hold?
  Re-derive it from the retained bundles."
- **Recorded verdict:** **NOT_READY (publication basis)**, non-gating.
  Sitting-packet seat table row, verbatim (`sitting-packet-FINAL.md:34`; header at `:21` =
  `lens | gating | verdict | coverage | blockers | should-fix | nits | falsifiers | unexec | ed-qual`):

  ```
  | L11-retained-characterization-basis | non-gating | NOT_READY | 14/16 | 0 | 3 | 2 | 5 | 6 | 0 |
  ```

  i.e. **0 blockers, 3 should-fix, 2 nits, 5 falsifiers, 6 unexecuted obligations, 0 ED-QUAL rows.**
- **Coverage:** 14/16 (`evidence_universe_count = 16`). Items 12 (a9 custody) and 16 (iCloud
  mirrors) partially examined.
- **Seat's own framing of its verdict (seat report line 10), verbatim:**
  > The quantitative chain **re-derives cleanly and the attribution-limited conclusion is robust**
  > (every number reproduced below, several bit-for-bit). What fails the exactness bar is the
  > paper's *framing* of the chain: the triple is presented as "the measured corpus figure" when it
  > is a single-member maximum plus a derived quotient, the phase evidence is attributed to a
  > window (a9) that holds no phase members, and the PASSED-verdict context survives only as prose.
  > All three are cheap, wording/retention-level fixes; none is a blocker; none touches the launch
  > GO (this seat is outside it).
- **Seat-report digest recorded in the sealed packet:** `484a6a0421fd421a`
  (`sitting-packet-FINAL.md:11`).

### What NON-GATING means for a READY-candidate aggregation — stated explicitly

1. **L11 IS counted in the headline 0/11.** `council-verdict.md:12` verbatim: "**NOT-READY. 0
   READY / 11 NOT-READY** (ten gating seats + the non-gating L11 basis seat)." The seat's
   NOT_READY is a real recorded verdict, not an advisory note.
2. **L11 is NOT part of the launch-GO aggregation.** Per charter amendment 13 (`charter:55-57`)
   the seat sits "outside the launch-GO aggregation"; the sitting packet's aggregation line
   (`sitting-packet-FINAL.md:36`) computes over the gating seats: "Raw aggregate: 1 READY / 10
   NOT_READY". The seat itself concurs: "none touches the launch GO (this seat is outside it)".
3. **Consequence for a READY-candidate sitting:** an unresolved L11 finding cannot, by charter,
   block arming a funded window — but it also is **not discharged by a launch GO**. Its findings
   are P1 **paper**-bearing (the capstone's central limitation exhibit), and the council routed
   them into the Phase-1 should-fix batch alongside the consistency sweep: "should-fix batch incl.
   sweep verify-and-fix items (B1 …, B2/B3 …, B6 README, B7 paper floor-regime row — P1
   claim-bearing) **and L11's three paper corrections**" (`council-verdict.md:85-87`). A seat
   should be explicit about which of the two questions it is answering: *may a window be armed*
   (L11 is silent) versus *may the paper be published as written* (L11 is the seat of record).

---

## 1. FINDINGS — original text verbatim, with citation

Source of the verbatim text below: `raw/L11-triage.md` (extracted from
`docs/process_traces/2026-08-15-readiness-council/triage.json`, seat entry
`L11-retained-characterization-basis`). Cross-cited to the sealed sitting packet and the seat
report (where the same findings are labelled SF1/SF2/SF3/N1/N2).

### F1 / SF1 — [should_fix]

**Title (verbatim):** Paper presents the ±31 ms / 33 W / ~1 J triple as 'the measured corpus
figure'; it is a single-member maximum plus a derived quotient

**file_line (verbatim):** `docs/paper/draft-v1.md:108 (also :7 abstract, :112 caption, :240)`

**failure_scenario (verbatim):**
> A metrology-literate referee asks which retained artifact records a 33 W power step. None does:
> composed anchor bounds across the 30 a10 phase members span 25.6–31.1 ms (mean 27.3; ±31 ms is
> the single widest member, prefill-abs-r01); operative phase envelopes span 0.57–1.57 J; '33 W' is
> that one member's envelope/bound quotient (1.016 J / 31.07 ms = 32.7 W), while corpus-wide
> quotients span ~21–58 W and r01's trace-measured prefill-vs-decode mean-power step is 18.6 W
> (45.6 → 27.0 W). The exhibit's conclusion survives, but 'corpus precision' / 'the measured corpus
> figure' overstates provenance and invites a credibility hit on the paper's central limitation
> exhibit.

**Citations:** `sitting-packet-FINAL.md:169`; seat report
`docs/process_traces/2026-08-15-readiness-council/seat-reports/L11-retained-characterization-basis-report.md:59`
(SF1). Positive re-derivation backing it: seat report §3 ("±31 ms", "~1 J", "~33 W").
**Post-verdict adjudication:** none — not among council-verdict Disposition 4's struck findings.

**Work order (verbatim, WO-1):**
> WO-1 (draft-v1.md:7,:108,:112,:240): restate the characterization as what the artifacts hold —
> composed clock-anchor bounds up to ±31 ms (25.6–31.1 ms across the 30 a10 phase members),
> per-member phase mis-attribution envelopes ~0.6–1.6 J (about one joule typical), equivalent to
> effective boundary power steps of tens of watts (e.g. 1.02 J / 31 ms ≈ 33 W for the widest-bound
> member) — or keep the triple but pin it explicitly to its defining member and derivation instead
> of calling it 'the measured corpus figure'.

### F2 / SF2 — [should_fix]

**Title (verbatim):** Paper attributes the phase mis-attribution evidence to 'the a9 and a10
windows'; a9 contains zero phase-absolute members

**file_line (verbatim):** `docs/paper/draft-v1.md:7, :108, :240`

**failure_scenario (verbatim):**
> A reviewer requests the a9 phase members backing the ±31 ms boundary characterization and finds
> only 7 request-level reference bundles (anchor bounds up to ±33.5 ms, which would even strain the
> ±31 ms headline if counted) plus a 12-member refcorpus. The phase-boundary basis is a10-only; a9
> is the reference/bracket-context window. The corpus framing as written cannot be backed
> member-for-member.

**Citations:** `sitting-packet-FINAL.md:170`; seat report line 61 (SF2); executed falsifier F3
(seat report line 54): "hunted a9 for any phase-absolute member → none exist (7 request-level refs,
bounds 30.0–33.5 ms, + 12 refcorpus)."

**Work order (verbatim, WO-2):**
> WO-2 (draft-v1.md:7,:108,:240): attribute the phase-boundary evidence to a10's 30 phase-absolute
> members, naming a9 as the reference/bracket-context window of the retained corpus rather than a
> co-source of the phase characterization.

### F3 / SF3 — [should_fix]

**Title (verbatim):** Whole-window PASSED verdicts for a9/a10 exist only as close-out prose; no
verdict artifact is retained anywhere findable

**file_line (verbatim):**
`~/JouleWise-window-custody/window_a10_20260725/CLOSE_OUT.md; detection-floor-extraction.json (refuses whole_window_neg8_verdict_missing)`

**failure_scenario (verbatim):**
> Anyone auditing the publication basis (this seat, a referee, or a future re-derivation) cannot
> produce the PASSED verdict ('excursions 0.509 J both families; 37-member basis c3a4f4e1...') from
> any retained artifact — not in the runs dirs, the bound dirs, the custody dir, the repo, or the
> iCloud archive mirror; the retained extraction itself refused for the verdict's absence. I
> re-derived the excursions exactly (0.5094 J both families for a10; 0.310/0.305 J for a9, all
> under allowances), so the fix is cheap: commit the re-derivation beside the custody close-out so
> the PASSED context is artifact-backed rather than prose-backed.

**Citations:** `sitting-packet-FINAL.md:171`; seat report line 63 (SF3) and line 47
(§3 "Whole-window PASSED (context)").

**Work order (verbatim, WO-3):**
> WO-3 (custody + repo): make the a9/a10 whole-window PASSED context artifact-backed — commit the
> excursion re-derivation (a10 0.5094 J both families vs 0.6523/0.6579 J allowances; a9 0.310/0.305
> J vs 0.624/0.609 J) beside the custody close-out, or recover the original verdict artifacts from
> wherever they were emitted; alternatively strip PASSED context from consuming docs.

### F4 / N1 — [nit]

**Title (verbatim):** a9 MANIFEST.sha256 lists ./backup.log, which is neither resident nor covered
by PRUNED.md's enumeration

**file_line (verbatim):**
`/Users/edr/code/JouleWise/runs_window_a9_20260724/MANIFEST.sha256 (last entry) vs PRUNED.md`

**failure_scenario (verbatim):**
> A strict manifest verification reports 29 missing entries where the prune note authorizes exactly
> 28 plists; the unexplained backup.log discrepancy costs an auditor time or seeds doubt about the
> prune's completeness. All 173 resident files re-hash clean.

**Citations:** `sitting-packet-FINAL.md:172`; seat report line 65 (N1).

### F5 / N2 — [nit]

**Title (verbatim):** Two D-054 decision-log prose details do not reproduce exactly from the
retained bundles

**file_line (verbatim):** `docs/decision_log.md:4674-4684 (D-054 attribution-limited amendment)`

**failure_scenario (verbatim):**
> The 'settled reference pair three hours apart agreed to 0.007 J' matches no unique retained pair
> (best ~3.7 h candidates agree to 0.0013–0.0019 J gross / 0.0080 J idle-sub), and 'fiducial 24.9
> ms (80–87%)' understates the actual fiducial share range (80–97% across the 30 members). Neither
> figure is paper-cited; risk is only that future prose inherits them as artifact-backed.

**Citations:** `sitting-packet-FINAL.md:173`; seat report line 67 (N2); executed falsifier F4
(seat report line 55).

**Work order (verbatim, WO-4):**
> WO-4 (optional bookkeeping): annotate a9 MANIFEST/PRUNED for the backup.log entry and correct the
> two D-054 prose figures (nits N1/N2).

### Unexecuted obligations (verbatim, all six)

> - Full power-trace re-integration for the remaining 29 a10 phase members (1/30 done exactly; the
>   other 29 envelopes were accepted from sha-bound summaries whose digests I verified against the
>   custody extraction).
> - Code audit of the reducer-side envelope method implementation
>   (common_trace_shift_plus_independent_edge_corners_v3) in joulewise/reduce.py — I re-derived its
>   output numerically for one member but did not read the implementation.
> - Deep audit of joulewise/whole_window.py verdict machinery (surveyed for schema/semantics only;
>   the verdict artifact itself is absent — finding SF3).
> - a9 custody operator logs (window-chain/calibration logs) read in detail; a10's were read.
> - campaign_log.jsonl deep audit and raw plist parsing for the reference members.
> - Byte-parity verification of the iCloud archive mirrors against local dirs (layout and existence
>   checked only; a9 parity rests on the PRUNED.md-documented verification).

Citation: `sitting-packet-FINAL.md:257-262`.

---

## 2. WHAT CHANGED SINCE 2026-08-15

### The carrier commit

**`36c9d78`** — "Should-fix batch: sweep B1/B2/B3/B6/B7 + council L11 paper corrections"
(2026-08-15, author Ed R). **ON-MAIN.** Body, verbatim (relevant line):

> L11 SF1-SF3: corpus triple pinned to member p2015-df-ph-prefill-abs-r01 (31.07 ms / 1.016 J /
> 32.7 W derived — lead bit-verified vs retained summary_metrics.json); a10-basis provenance fixed
> at all sites; whole-window PASSED prose now carries the re-derivation basis.

Files touched: `.github/workflows/d117-production-proof.yml`, `README.md`, `TASK_QUEUE.md`,
`docs/decision_log.md`, **`docs/paper/draft-v1.md` (+18/−… , net 18 changed lines)**,
`docs/phase_2/alpha_arm_readiness.md`.

Subsequent paper commits that carried the corrections forward without reverting them: `c0ee784`,
`0a216b7`, `6f4b553` (all ON-MAIN); `53e480e` ("Instrument guide + paper: current-state
enrichment…") and **`2952226`** ("Plain-language pass (Ed directive): unpack stacked jargon across
the paper + guide's densest spots; **numbers and claims frozen**; REPLACE-EXACT anchors preserved")
— both **BRANCH-ONLY**. Also branch-only: `3efea49` (instrument-guide rewrite), `76f6861`
(consistency-sweep must-fixes).

### SF1 — LANDED. Current text at the cited locations (read at `b92b43d`)

Line numbers moved (plain-language pass); the substance is present at all four sites.

- **`docs/paper/draft-v1.md:118`** (was `:108`) — verbatim excerpt:
  > Across the 30 phase-repeatability runs of window a10, the combined bound on where a phase edge
  > may fall spans 25.6–31.1 ms. Dividing each run's phase-energy envelope — the width of the energy
  > interval that timing bound leaves open — by that run's own bound gives 21–58 W; **these are
  > quotients we computed, not power steps anyone measured**. The ten ordinary prompt-processing
  > runs have envelopes of 0.98–1.47 J. The familiar ±31 ms / ~33 W / ~1 J illustration comes from
  > one particular run, `p2015-df-ph-prefill-abs-r01`: its 31.07 ms bound and 1.016 J
  > prompt-processing envelope give a quotient of 32.7 W.
- **`docs/paper/draft-v1.md:122`** (Fig. 2 caption, was `:112`) — verbatim:
  > *Figure 2. Schematic; every value drawn in the figure is illustrative, not a measured corpus
  > triple. The sampler reports each interval's total energy, so shifting the boundary re-labels
  > only the energy inside the straddling band; the mis-attributed amount is bounded by the
  > boundary shift times the power change across it. In the retained a10 phase runs, the combined
  > timing bounds span 25.6–31.1 ms, each run's energy envelope divided by its own bound gives
  > 21–58 W, and the ordinary prompt-processing envelopes span 0.98–1.47 J.*
- **`docs/paper/draft-v1.md:258`** (§7 Attribution-limited resolution, was `:240`) — verbatim
  excerpt:
  > Across the 30 phase-repeatability runs of window a10, the combined bound on that placement
  > spans 25.6–31.1 ms; each run's phase-energy envelope divided by its own bound gives 21–58 W;
  > and the ordinary prompt-processing envelopes span 0.98–1.47 J. … Those watt figures are
  > quotients we computed, not power steps anyone measured …
- **`docs/paper/draft-v1.md:7`** (abstract) — see SF2 below (same sentence carries both fixes).
- The phrases the finding objected to — **"the measured corpus figure"** and **"at corpus
  precision"** — return **zero** grep hits in the current `docs/paper/draft-v1.md`.
- A §7 lead-in was added by `36c9d78` (then re-worded by the plain-language pass). Current text at
  **`docs/paper/draft-v1.md:252`**, verbatim:
  > The attribution-limited resolution item below quotes the full range of what was retained,
  > rather than presenting one run's largest bound and its derived quotient as though they
  > described the whole corpus. It explains why boundary placement, rather than run-to-run scatter,
  > is what this implementation has to attack first.

### SF2 — LANDED. Current text

- **`docs/paper/draft-v1.md:7`** (abstract) — verbatim excerpt:
  > The characterization retained here supports no claim of its own. It comes from 30 runs in
  > window a10 that repeat a single phase, with window a9 supplying reference and
  > bracketing-calibration context: the combined bound on where a phase edge may fall spans
  > 25.6–31.1 ms, and the phase energy this leaves uncertain is on the order of a joule.
- **`:118`** — "Window a9 supplies reference and bracketing-calibration context but contains no
  phase-repeatability runs."
- **`:258`** — "Window a9 supplies reference and bracketing-calibration context but no phase runs."
- The `36c9d78` diff also added to the publication-label subsection: "The retained characterization
  motivating this label comes from a10's 30 phase-absolute members; a9 contributes reference and
  bracket context only, and the figure's ±30 ms / 33 W / 1 J values remain illustrative."

### SF3 — LANDED **AS PAPER TEXT ONLY**; WO-3's primary remedy NOT executed

- **Paper text added** (new paragraph, `36c9d78`), current at **`docs/paper/draft-v1.md:137`**,
  verbatim:
  > The original whole-window verdict files for a9 and a10 were not kept. The reference runs that
  > were kept do, however, re-derive the drift figures exactly: the largest excursion for a10 is
  > 0.5094 J on total energy and 0.5094 J on idle-subtracted energy, against allowances of 0.652
  > and 0.658 J; for a9 the excursions are 0.310 and 0.305 J against allowances of 0.624 and 0.609
  > J. Any statement that those drift screens passed therefore rests on this re-derivation rather
  > than on a preserved verdict file.
- **WO-3's first option — "commit the excursion re-derivation … beside the custody close-out" — was
  NOT executed.** `~/JouleWise-window-custody/window_a10_20260725/` still contains exactly
  `CLOSE_OUT.md` (mtime **2026-07-25 06:54**), `detection-floor-extraction.json` (2026-07-25
  06:37), `operator_logs/`, `quarantine/`. `~/JouleWise-window-custody/window_a9_20260724/`
  contains only `operator_logs/` and `quarantine/`. No re-derivation artifact, script, or
  transcript was added to either.
- **WO-3's second option — recover the original verdict artifacts — no evidence located.**
- **WO-3's third option — "strip PASSED context from consuming docs" — was applied to the paper
  but NOT to the other consuming surfaces.** Grep for `0.5094` repo-wide returns exactly one live
  document hit: `docs/paper/draft-v1.md:137`. Meanwhile:
  - `docs/decision_log.md` D-054 clause 11 still reads, uncaveated: "The first collection under the
    merged SCREEN+BUDGET rules (**windows a9, a10; both whole-window verdicts PASSED**) could not
    produce a floor…"
  - `README.md:103` still reads: "That protocol ran five times and **passed five times** — windows
    C, D, a10, the 7B floor window, and the contrast window — under the merged screening and
    uncertainty-budget rules (D-078 clause 10)." No re-derivation caveat.

### N1 — NO REPAIR FOUND

`/Users/edr/code/JouleWise/runs_window_a9_20260724/MANIFEST.sha256:202` still reads
`8c239ebaa49dd65dd242af07741c3d96685b7a4b017335587ea2e5a21ed264af  ./backup.log`. `PRUNED.md` in
the same directory has no `backup` mention (grep). Both files' mtime is **2026-07-28 05:29** —
untouched since before the council.

### N2 — NO REPAIR FOUND

`docs/decision_log.md` D-054 clause 11 still carries both figures verbatim:
- "(and a settled reference pair three hours apart agreed to 0.007 J)" (`:4688-4689`)
- "fiducial 24.9 ms (80-87%) plus bundle-local 3.3-6.1 ms" (`:4693`)

`git log -S"0.007 J" 8937dec..HEAD -- docs/decision_log.md` returns **empty** — no commit since the
audit baseline touched that string.

### Adjacent sweep items that the council routed with L11's corrections

- **B7 (P1 claim-bearing, "paper floor-regime row")** — sweep finding verbatim heading
  (`consistency-sweep-findings.md:75`): "B7. The paper's mainline floor regime contradicts the
  frozen instrument, and the swap block has no live owner"; its prescribed fix: "register the
  CONDITIONAL-INSERT-TIGHTER-FLOOR swap as a live queue row (P1, owner + trigger = first
  post-freeze mint) or execute the mechanical swap now."
  **LANDED (registration branch), ON-MAIN via `36c9d78`.** Live row at **`TASK_QUEUE.md:246`**,
  verbatim excerpt:
  > | CONDITIONAL-INSERT-TIGHTER-FLOOR | P1 Phase Gate | [AGENT] | **LIVE — trigger pending** |
  > Lead | First post-freeze mint under the frozen 1.869502 J selector | … At the trigger, apply
  > the complete `CONDITIONAL-INSERT-TIGHTER-FLOOR` replacement block in `docs/paper/draft-v1.md`
  > as one paper-consistency transaction and verify every replacement against the minted artifact.
  > Do not apply a partial swap; issued result and floor-regime numbers change only at that mint.
  > **The council-ordered L11 provenance corrections to characterization prose are separately
  > authorized and already applied.** |

  Paper side, current `docs/paper/draft-v1.md:272` (and the swap-block copy at `:404`), heading
  changed from "**not yet consumed**" to "**registered for the next mint**", with:
  > Results in this cycle's retained corpus were issued under the conservative 8.611855 J
  > composition; the complete paper-regime swap executes at the first post-freeze mint tracked in
  > `TASK_QUEUE.md` and has not been applied here.

  **NOTE FOR THE SEAT:** the row's trigger is "First post-freeze mint under the frozen 1.869502 J
  selector". The `freeze-0003` mints for the three `_v3` packs executed on 2026-08-19 (`5e38f1e`,
  `eb7f6c6`, `94dc3b3`, table at `8b2b021` — all BRANCH-ONLY). Whether those are "the first
  post-freeze mint" in the row's sense (a **floor** mint) or merely freeze-receipt mints is a
  question the assembler cannot settle. The row is still `LIVE — trigger pending`.
- B1 (`alpha_arm_readiness` re-anchor), B2/B3 (queue closures + D-130 disposition), B6 (README
  blurb) — all recorded as landed in the same commit body; `docs/phase_2/alpha_arm_readiness.md`
  shows the largest single-file change in `36c9d78` (195 lines).

### The r5 → r6 supersession (post-dates every L11 fix)

- **`76f6861`** (BRANCH-ONLY) — "Consistency sweep must-fixes: **r5→r6 supersession recorded**
  (ruling amendment 15-amendment-r6.md, D-145/D-147 rows, RUN_STATE banner), README volatile count
  removed per policy, CLAIMS_STATUS mechanical-barrier note, WINDOW_STATUS evidence-expiry hazard,
  packet head update, guide bind-at-birth precision".
- Authority: `docs/process_traces/2026-08-19-r1-r2-codesign/15-amendment-r6.md` — "the `_v3` family
  binds **r6** at birth"; "r5 remains registered, byte-identical history — exactly as r3/r4."
- **Paper citations checked:** `docs/paper/draft-v1.md` cites
  `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json` at `:52`, `:64`, `:189` and
  `ACTIVE_ACCEPTANCE_ID = r6` at `:64`. **No `_n17_r5` citation remains in the paper.**
- **ONE STALE ARTEFACT LOCATED.** `docs/paper/draft-v1.md:189` ends its verification comment with:
  > NOTE: freeze-0003 itself is not yet minted
  This is **false at `b92b43d`**: freeze-0003 was minted for all three `_v3` packs on 2026-08-19
  (`5e38f1e`, `eb7f6c6`, `94dc3b3`) with the S5 confirmation table filled at `8b2b021`.

### The capture-era claim barrier (D-146) and the anchor-v2 registered limitation (D-148.7)

Both post-date L11's audit and bear directly on the corpus the seat certified.
`CLAIMS_STATUS.md:3-19`, verbatim:

> **Era update (2026-08-19):** exclusion of pre-anchor-v3 evidence from claims is now enforced
> MECHANICALLY by the instrument (the capture-era claim barrier, D-146) — not only by the protocol
> decisions recorded below. Every corpus collected before the anchor-v3 production flip is
> non-claim-bearing under the current instrument; fresh collection under the `_v3` family is the
> claim path.
>
> **Registered limitations (Ed rulings D-148.6/.7, 2026-08-19):** (a) the stored anchor-v2
> population — 748 bundles in the repository tree — is PERMANENTLY non-claim-bearing on estimator
> grounds (the v2 rate=1 model was falsified); replay/audit value retained forever; enforcement is
> the mechanical D-146 claim barrier. … Both belong in the paper's limitations section — the
> anchor-v2 paragraph is already drafted there.

Barrier implementation (BRANCH-ONLY, `b7e5730` "S1: anchor-v3 production flip + D-079 r5 … + claim
barrier (D-146)"); refusal code `capture_pipeline_absent` registered at
`joulewise/whole_window.py:199`, `joulewise/floor_extraction.py:190`,
`joulewise/analysis_engine/claims.py:135,173`, `joulewise/uncertainty_evidence.py:1312-1321`,
`joulewise/controller.py:1362`.

---

## 3. ED-QUALIFICATION ROWS

**No ED-QUALIFICATION rows were emitted by this seat.** The sitting packet records `ed-qual = 0`
for L11 (`sitting-packet-FINAL.md:34`), and the seat report states it directly (§7, line 75):

> None — this seat required no hardware, sudo, or live measurement; the entire chain re-derived at
> the desk from retained artifacts.

**Did later work create one?** **No L11-owned ED row was located.** Searched: `raw/L11-triage.md`
§ED-QUALIFICATION ROWS (empty); `sitting-packet-FINAL.md` §ED-QUAL list (L11 absent);
`RUN_STATE.md` ED-OWED lists at `:459` and `:546`; `docs/process/ed-batch-packet.md`;
`docs/process/ed-evening-checklist.md`. The Ed-owed lists contain an **a9/a10 desk replay** item —
but that is **ED-L10-1**, the L10 sacrificial-lifecycle seat's row (post-collection chain against
the retained corpus), not an L11 row; L11's own chain re-derived without Ed.

**Adjacency worth flagging to the seat, not asserted as an L11 obligation:** ED-L10-1's replay runs
the whole-window verdict against the same retained a9/a10 corpus. If executed, it would produce
exactly the artifact SF3 says is missing. It has **no located closure evidence** (see ROW-L10 §3).

---

## 4. CANDIDATE DISPOSITIONS FOR THE SEAT TO ADJUDICATE

**Candidate dispositions are assembled, not adjudicated; the seat rules.**

| Item | Sev. | Candidate disposition | What the seat is adjudicating |
|---|---|---|---|
| **SF1** triple presented as corpus figure | should-fix | **REPAIR-EVIDENCE-ATTACHED (text quoted)** | The offending phrases are gone; ranges (25.6–31.1 ms / 21–58 W / 0.98–1.47 J) and the pinned member `p2015-df-ph-prefill-abs-r01` are in the abstract, §body, Fig. 2 caption and §7. Seat weighs whether the rewrite matches WO-1's demand and whether the plain-language pass (`2952226`, BRANCH-ONLY) preserved it faithfully. |
| **SF2** a9 attributed as phase source | should-fix | **REPAIR-EVIDENCE-ATTACHED (text quoted)** | All three cited sites now name a10's 30 phase runs as the basis and a9 as reference/bracket context. Seat weighs completeness across the paper, guide, and figure assets. |
| **SF3** PASSED verdict is prose-only | should-fix | **PARTIALLY REPAIRED — third remedy applied to ONE consuming doc; primary remedy not executed** | The paper now discloses the absence and carries the re-derivation (`:137`). But no artifact was committed beside the custody close-out (custody untouched since 2026-07-25), no original verdict was recovered, and the uncaveated PASSED prose survives in `docs/decision_log.md` D-054 cl.11 and `README.md:103`. |
| **N1** a9 MANIFEST `./backup.log` | nit | **STILL-OPEN / NO-REPAIR-FOUND** | Files unmodified since 2026-07-28; WO-4 was optional. |
| **N2** two D-054 prose figures | nit | **STILL-OPEN / NO-REPAIR-FOUND** | Both strings verbatim present; no commit since baseline. |
| **6 unexecuted obligations** | — | **NO CLOSURE EVIDENCE LOCATED** | Notably (a) 29/30 trace re-integrations, (b) the reducer envelope-v3 code audit, (c) the `whole_window.py` deep audit — the last being the machinery whose missing artifact is SF3. |
| **B7 paper floor-regime row** (routed with L11's corrections) | blocker (sweep) | **REPAIR-EVIDENCE-ATTACHED (registration branch), TRIGGER PENDING** | Live P1 row exists (`TASK_QUEUE.md:246`) and the paper's stale "not yet consumed" claim was corrected. Seat weighs whether the 2026-08-19 `freeze-0003` mints fired the row's trigger. |
| **New (post-L11) — paper note contradicted by the transaction** | — | **NEW ITEM, NOT ADJUDICATED AT 2026-08-15** | `docs/paper/draft-v1.md:189` still asserts "NOTE: freeze-0003 itself is not yet minted"; freeze-0003 was minted 2026-08-19 (BRANCH-ONLY). |

---

## 5. WHAT A SKEPTICAL SEAT SHOULD PROBE

1. **[MANDATORY — does any published or paper number still trace to a voided or superseded
   corpus?]** The retained a9/a10 corpus is pre-anchor-v3 and is now **mechanically** barred from
   claims by D-146, with D-148.7 making the stored anchor-v2 population "PERMANENTLY
   non-claim-bearing on estimator grounds" (`CLAIMS_STATUS.md:3-19`). The paper's characterization
   is explicitly non-claim ("The characterization retained here supports no claim of its own",
   `:7`) — **but the floor-regime numbers are not.** `8.611855 J` and `1.869502 J` are described as
   coming from "the retained token-generation contrast cell" at `:258`, `:272`, `:367`, `:375`,
   `:391`, `:399`, `:404`.
   *Probe:* for each of those seven sites, name the source corpus and its capture era; then run the
   D-146 barrier against that corpus.
   *Falsifier:* a document showing those cells' evidence is anchor-v3-era, **or** a recorded ruling
   licensing pre-v3 numbers as prospective-sizing scale (as distinct from claims). Absent either,
   the paper carries superseded-corpus numbers in non-caveated form.
2. **[MANDATORY — did r5→r6 leave stale figures?]** The paper cites the `r6` acceptance artifact at
   `:52`, `:64`, `:189` and no `r5`. But `:189`'s own verification comment ends "**NOTE:
   freeze-0003 itself is not yet minted**", which the S5 commits falsify.
   *Probe:* `grep -n 'not yet minted\|freeze-0002\|_n17_r5' docs/paper/draft-v1.md docs/*.md
   README.md CLAIMS_STATUS.md WINDOW_STATUS.md PROJECT_STATUS.md`.
   *Falsifier:* a later commit correcting that note. The consistency sweep that recorded the
   supersession (`76f6861`) did not catch it.
3. **Is SF3 actually discharged, or only disclosed in one place?** WO-3 offered three remedies; the
   executed one ("strip PASSED context from consuming docs") was applied to the paper only.
   *Probe:* `grep -rn 'verdicts PASSED\|passed five times\|both whole-window verdicts'
   docs/decision_log.md README.md PROJECT_STATUS.md CLAIMS_STATUS.md WINDOW_STATUS.md`.
   *Falsifier:* a caveat at `docs/decision_log.md` D-054 cl.11 and `README.md:103`. As read, both
   still assert PASSED without pointing at the re-derivation.
4. **Is the re-derivation itself reproducible by anyone but the seat?** The numbers now printed in
   the paper (`0.5094 / 0.5094 / 0.310 / 0.305 J` vs `0.652 / 0.658 / 0.624 / 0.609 J`) exist in
   exactly one live location — `docs/paper/draft-v1.md:137` — with no committed script, transcript,
   or artifact.
   *Probe:* ask for the derivation script/inputs by path; attempt an independent re-derivation from
   `runs_window_a9_20260724[_bound]` / `runs_window_a10_20260725[_bound]`.
   *Falsifier:* a committed re-derivation artifact. **The paper has thus moved from prose-backed
   PASSED to prose-backed re-derivation** — a seat should decide whether that satisfies WO-3.
5. **Did the plain-language pass silently move a number?** `2952226` claims "numbers and claims
   frozen" but rewrote the same paragraphs L11 had just corrected (BRANCH-ONLY, so it is *not* on
   main).
   *Probe:* `git diff 36c9d78..b92b43d -- docs/paper/draft-v1.md | grep -E '^[+-].*[0-9]+\.[0-9]{3}'`
   and diff the number set before/after.
   *Falsifier:* any numeric delta in the SF1/SF2/SF3 paragraphs. Note the corrected text now says
   "The ten ordinary prompt-processing runs have envelopes of 0.98–1.47 J" where the seat's own
   report said the prefill cell spans 0.98–1.47 J across the corpus — confirm the "ten" is
   artifact-backed, since the seat's report does not state a count of ten.
6. **Do the ranges themselves survive the seat's own unexecuted obligations?** L11 re-integrated
   1 of 30 traces exactly and took the other 29 envelopes from sha-bound summaries; it did not read
   `common_trace_shift_plus_independent_edge_corners_v3` in `joulewise/reduce.py`. The paper now
   publishes those 29-member-derived ranges as its stated basis.
   *Probe:* re-integrate two or three additional a10 members from raw traces.
   *Falsifier:* any member whose recomputed envelope falls outside 0.98–1.47 J (prefill) or whose
   composed bound falls outside 25.6–31.1 ms.
7. **Did `reduce.py` change under the r5/r6 reissue in a way that moves the retained envelopes?**
   The r6 amendment records that S1 fix round 2 (`3038eeb`) "edited
   `joulewise/uncertainty_evidence.py` and `joulewise/reduce.py` — two of the four D-079-pinned
   estimator sources" (`15-amendment-r6.md`), forcing a science-neutral reissue proven over a
   **19-member** replay.
   *Probe:* was the a10 30-member phase corpus inside that neutrality replay, or only the D-079
   calibration corpus? Read
   `docs/process_traces/2026-08-19-refreeze-execution/r6-issuance/r6-neutrality-proof.json`.
   *Falsifier:* the replay covers the a10 phase members. If it does not, the paper's 25.6–31.1 ms /
   0.98–1.47 J ranges were derived under a **different** reducer than the one now at head, and
   nothing has re-verified them.
8. **N1/N2 residual risk is exactly the one L11 named.** N2's failure scenario was "risk is only
   that future prose inherits them as artifact-backed". Between 2026-08-15 and now the paper and
   the instrument guide were rewritten three times (`53e480e`, `3efea49`, `2952226`).
   *Probe:* `grep -rn '0.007 J\|80-87\|80–87\|24.9 ms' docs/paper/ docs/*.md` .
   *Falsifier:* any occurrence of the unreproducible figures in newly written paper or guide prose.

---

## 6. OPEN ITEMS FROM THIS ROW

- **SF3's primary remedy was not executed.** No excursion re-derivation artifact was committed
  beside the custody close-out: `~/JouleWise-window-custody/window_a10_20260725/` still holds only
  `CLOSE_OUT.md` (mtime 2026-07-25 06:54), `detection-floor-extraction.json`, `operator_logs/`,
  `quarantine/`; the a9 custody directory holds only `operator_logs/` and `quarantine/`. The
  a9/a10 PASSED context is now **prose-backed re-derivation** in one paper paragraph
  (`docs/paper/draft-v1.md:137`) rather than artifact-backed.
- **Uncaveated PASSED prose survives in two consuming documents** that WO-3's third option would
  have covered: `docs/decision_log.md` D-054 clause 11 ("windows a9, a10; both whole-window
  verdicts PASSED") and `README.md:103` ("That protocol ran five times and passed five times —
  windows C, D, a10, …").
- **N1 unrepaired.** `runs_window_a9_20260724/MANIFEST.sha256:202` still lists `./backup.log`;
  `PRUNED.md` still does not mention it; both files unmodified since 2026-07-28 05:29.
- **N2 unrepaired.** `docs/decision_log.md` D-054 clause 11 still carries "a settled reference pair
  three hours apart agreed to 0.007 J" and "fiducial 24.9 ms (80-87%)"; zero commits since the
  audit baseline touched either string.
- **A new stale assertion has appeared in the paper since the corrections landed:**
  `docs/paper/draft-v1.md:189` states "NOTE: freeze-0003 itself is not yet minted", contradicted by
  the S5 mints (`5e38f1e`, `eb7f6c6`, `94dc3b3`) and the filled confirmation table (`8b2b021`), all
  BRANCH-ONLY on `impl/r2-s0-mint-resolver`. The 2026-08-19 consistency sweep (`76f6861`) that
  recorded the r5→r6 supersession did not catch it.
- **All six of L11's unexecuted obligations remain without located closure evidence**, including
  the `joulewise/whole_window.py` deep audit (the machinery behind the missing SF3 artifact), the
  reducer envelope-v3 code audit, and the 29 outstanding exact trace re-integrations — the last two
  now underwriting ranges the paper publishes as its stated basis.
- **Corpus-era question unresolved by any located document:** the a9/a10 basis is pre-anchor-v3 and
  mechanically barred from claims by D-146/D-148.7, while the paper's floor-regime numbers
  (8.611855 J, 1.869502 J) are still sourced to "the retained token-generation contrast cell" at
  seven sites. No located ruling distinguishes prospective-sizing use from claim use for that cell.
- **Neutrality-replay scope unresolved:** the r6 science-neutrality proof is a 19-member replay
  over the D-079 calibration corpus; the assembler could not establish whether the a10 30-member
  phase corpus — whose envelopes the paper now publishes — was inside it, despite `reduce.py` being
  edited in the same transaction (`3038eeb`).
- **Where the evidence lives is split.** L11's three corrections and the B7 row are **ON-MAIN**
  (`36c9d78`). Every subsequent paper/guide rewrite that carried them (`53e480e`, `3efea49`,
  `2952226`) and the whole r5→r6 / freeze-0003 transaction are **BRANCH-ONLY**.
- **Read-tree discrepancy:** the task named `4597ad4`; the worktree is at its child `b92b43d`.
