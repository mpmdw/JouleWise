# Fresh-reviewer audit: the paper and the research questions

Reviewer: independent Fable 5.1 seat, no loop context, read-only. Repo
`/Users/edr/code/JouleWise` at `b81a2ac5` (main), 2026-09-02. Two lenses:
program-committee reviewer and capstone advisor (metrology, JouleSort).

What was read: `docs/paper/draft-v2-skeleton.md` in full (1790 lines;
11,575 main-text words + 6,803 appendix words after stripping build notes);
`docs/paper/draft-v1.md` front matter and references; every file in
`docs/paper/round7/` (heads, conclusions, the DG-071/075 artifact in full);
`docs/paper/results-fill-registry.md` (rules, status census, rows DG-027,
DG-067..077, DS-02, DS-34, V5-G2A-001); `docs/research_question_registry.md`
and `docs/research_question_coverage-2026-08-28.md` in full; the bank outline;
`docs/publication_release_checklist.md`; `docs/advisor_briefs/2026-07-30-advisor-brief.md`;
`docs/process/rivoire-meeting-brief-2026-08-18.md`; the T26 paper-goal ruling;
the 08-28 blind reviewer-panel synthesis; the 09-01 fresh-model review (Sol
paper/RQ seat + magistrate synthesis + Opus pedagogy seat); the 08-31 final
pre-data adjudication; PRs #270, #271, #276 (`gh pr view`); all 43 trace files'
index in `docs/process_traces/2026-09-02-paper-d-dg071/` plus
`MAGISTRATE-NOTES.md`; the `_v5` kernel rows; `CLAIMS_STATUS.md`,
`RUN_STATE.md` T26–T30, the 09-02 pause state on the decode-identity worktree.

What was executed this session (bench evidence, not quoted from docs):
`python3 -m unittest tests.test_paper_first_use_ledger tests.test_docs_freshness`
-> `Ran 26 tests ... OK`; a first-occurrence scan of ~150 candidate terms over
the comment-stripped body of the v2 skeleton (script inline, results in §4
below); `ls runs_*` (36 retained corpora on disk, all pre-anchor-v3);
`gh pr view 239` -> OPEN, title "HOLD MERGE until _v4 closes";
`python3 scripts/check_paper_round7_artifacts.py` -> `R7F COMPARED 184 /
MISMATCHES 0`; `PAPER_REPLAY_CORPUS_ROOT=... scripts/check_paper_replay_fence.py`
-> `COMPARED 43 / MISMATCHES 0` (the retained capture's numbers in §2 replay
byte-for-byte).

---

## 1. What the paper currently claims, and what backs it

### 1.1 The claim structure (v2 skeleton)

The successor draft has one primary research question, one demonstration,
one printed negative, and three contributions:

| Claim | Where | Status of backing |
|---|---|---|
| Primary: allowed phase-edge movement at least doubles every source of false phase-energy difference — `R = U_corner/U_point >= 2` per component per cell, and comparative `R_cm >= 2`, else the dominance sentence is withdrawn | §1 `draft-v2-skeleton.md:112-124`; §4 `:493-512`, `:630-640`; outcome forms `:788-808` | PLACEHOLDER. Eight `R_*` keys + four `R_cm_*_cmp` keys are `[FILL]` (`:812-843`, `:895-906`). No `_v5` data exists. |
| Demonstration: fixed Qwen3-1.7B vs Qwen3-8B, decode (real_prompts_v1, greedy, 512) and prefill at a G2-a-selected length; two-gate decision (magnitude vs cell floor; direction via measurement + decision interval, Holm m=2) | §1 `:126-142`; §4 `:698-786`; §6 `:895-906` | PLACEHOLDER. DS-09..DS-33, PG-01..PG-08, V5-G2A-001, V5-WL-005 all STOP_FILL. Prefill length itself unresolved until G2-a. |
| Printed negative: 37 of 50 short-prefill phases overlapped only two sampler records (< 3) and are `not resolvable` | §1 `:144-149`; §6 `:917-940` | BACKED by retained diagnostic data (DG-067/068/069/076/077 = 37/50/13 MEASURED, `results-fill-registry.md:639-649`; DG-071/075 issued today by #276: median width 120.9186 ms, IQR 5.9508 ms; spacing 120.9224 / 5.8949 ms). BUT the §6 prose is still a build note — zero reader-facing sentences. |
| Contribution 1: in-window pulse-train calibration with the corrected (rate-aware) clock anchor; bracket rule (10.164835 ms max pre/post difference; 9.724 ms minimum allowance; `b = max(B_pre,B_post) + max(|B_post-B_pre|, 9.724 ms)`) | §2 `:161-177`; A.3 `:1260-1529` | BACKED by the retained 17-capture corpus (A.3.8 `:1503-1529`), the worked capture `20260722T145535-e941c821` (`:181-197`, replay-fenced 43/43), and two round-7 desk analyses not yet cited in the paper: `round7/anchor-correction-quantified.md` §6 (2 of 14 previously-admitted captures are refused by the corrected anchor; numerical change median 0.61 %, max 4.05 %) and `round7/excursion-decomposition.md` (the 30 ms bound = ~13 ms repeatable onset bias + worst-pulse excess + reach + 1.1 ms anchor; Figure 4 exists at `figures/fig4_edge_excursions.svg`). All diagnostic-era. |
| Contribution 2: the cell-specific resolution bound (cell floor) and the dominance ratio | §4 `:641-700` | Formulae and a retained two-block fixture (`R_cm = 3.633`, `:600-640`) — arithmetic only. Pilot ratios 10.92 / 5.92 / 7.02 (`:370-395`, `:520-531`) are retired-calculation evidence, explicitly not campaign results. |
| Contribution 3: decision behaviour — fail-closed admission, printed refusals, the resolvability rule | §5 `:845-875` | Backed by code and by one retained refusal case (`:868`); the numeric thresholds are concrete and replicable. |
| Four instrument characterizations (workload response, identical-condition null, phase accounting, drift/recovery) | §3 `:205-309`, `:356-364` | ALL STOP_FILL (DS-02/03/05/06). The `_v5` transaction does not produce them: the retensing plan carries "Outcome D — identical-workload characterization not collected" (`round7/retensing-plan.md`, Outcome definitions). §3 therefore promises four results the campaign will not deliver. |

Claim-eligible collected data: **none**. `CLAIMS_STATUS.md:73-75` ("VALID —
minted, mainline, citable: NONE"); every corpus on disk (36 `runs_*`
directories, 2026-07-18 to 2026-08-04) predates the anchor-v3 production flip
and is mechanically non-claim-bearing under D-146. The a9/a10 "PASSED"
verdicts in memory are Qwen2.5 diagnostic-era windows, not `_v5`.

Placeholder census: 115 `[FILL:...]` markers in the skeleton (my count, `grep
-o '\[FILL:[^]]*\]' | wc -l`); registry census 75 STOP_FILL rows, 39
SUPPLIER_UNKNOWN, 109 VALUE_UNISSUED, 114 MEASURED (diagnostic-era), 29
ISSUED. Sections that are still build notes rather than prose: Abstract
(`:23-80`), §6 Results order (`:882-889`), §6 negative result (`:917-940`), §6
demonstration (`:942-955`), §7 "What the finding changes" (`:998-1004`), §9
(`:1209-1220`), §10 (`:1222-1230`), §11 References (`:1232-1235`, empty; v1
carries 31 entries of which 21 are cited in v2 §8), A.6 (`:1541-1549`).

### 1.2 What landed today (PRs #270, #271, #276)

- #270: §7 threats/limitations/future work + D6–D11 reviewer sentences
  (`:1006-1181`). Notably honest: the inserted-gap fiducial is stated to be "a
  proposed design, not yet a runnable protocol: its sleep actuation,
  command-stamp method, and fitted-edge selection remain to be fixed"
  (`:1137-1141`).
- #271: §1 introduction and §3 characterization/pilot prose; ledger 220 terms,
  FAILS 0; survival-map DG-059–066 relabel.
- #276: the DG-071/075 producer, a 43-file gauntlet, values of record above;
  registry rows and fill-checklist sentences still to be flipped (PR body
  "Follow-ups NOT in this PR").

### 1.3 The `_v5` path to a filled paper is longer than "one window"

Kernel chain (`state_kernel.json`): `V5-G2A-PREFILL-PROBE-01` (queued,
quiet_mac) -> `V5-DESK-DAY-01` (blocked) -> `V5-G2B-SHAKEDOWN-01` (blocked)
-> `V5-TRANSACTION-GO-01` (Ed, blocked) -> `V5-TRANSACTION-01` (blocked) ->
`TRANSFER-FIDUCIAL-01` (blocked, PR #239 open and held) -> `V6-SCORED-LEG-01`.
That is at least three machine evenings (G2-a, G2-b, transaction) before the
first claim-bearing byte, plus the fiducial night. `docs/process/v5-artifact-flow.md`
"What does not exist yet" still lists: no `_v5` extraction spec in the pack;
no `_v5` final pinset / v2 input manifest; no results-fill adapter
(`RENDERER-V5-SUCCESSOR-01`, blocked). The dominance close-out core exists on
main (`joulewise/dominance_closeout.py`, D-168) but its consumer chain to the
paper is not closed. `V5-DECODE-IDENTITY-SET-01` is `partial` on a branch with
a fourth same-signature prose defect escalated (pause state file 39).

---

## 2. Research questions: now / one window / cut

Coverage doc counts (`research_question_coverage-2026-08-28.md:170-180`): 89
rows; 2 answered by `_v5`, 9 answerable at the desk, 41 answerable but
unrouted, 17 not answerable with this instrument, 18 not questions, 2 for
`_v6`.

### 2.1 Answerable from data already on disk (diagnostic-era, publishable as instrument characterization, never as a claim)

| Row | Evidence | Paper state |
|---|---|---|
| RQ-SHORT-PREFILL-RESOLVABILITY (37/50) | `process_traces/2026-08-09-prefill-phase-proof/`; DG-067..077 MEASURED; DG-071/075 issued | Build note only (`:917-940`). Writable today. |
| RQ-METHOD-FLOOR as a mechanism (the calibration corpus: 17 bounds 23.2–32.9 ms; the 118-edge decomposition; the anchor-correction admissibility result 2/14) | A.3.8; `round7/excursion-decomposition.*`; `round7/anchor-correction-quantified.*` | §2/A.3 carry the corpus; the two desk analyses are NOT cited in the paper (grep "Figure 4", "anchor-correction": only a comment at `:395`). |
| RQ-AUDITABLE-EVIDENCE (L1) | strict validation + evidence chain | §5, A.2 — but "not presently open to independent re-reduction" (`:1239`, `:1116-1124`). |
| C5-1.5, C5-1.10, C5-1.11 (partial: recovery tails, refusal frontier, ANE-dark) | retained windows | Mentioned only as method/limitation. Correctly not promoted. |
| RQ-QWEN25-SMOKE, RQ-QWEN35-SMOKE, RQ-TWO-MODEL-ACTIVE-NONCLAIM, RQ-MLX-KV-REPLAY | run reports | Not in the paper; leave out. |

### 2.2 Need exactly one more window (or one chain of windows)

| Row | What it needs | Honest cost |
|---|---|---|
| RQ-ATTRIBUTION-DOMINANCE (primary) | the `_v5` alpha + beta floor windows and gamma contrast; close-out chain built | G2-a evening + desk day + G2-b + transaction; desk gaps in §1.3 |
| C5-1.1 at its pairwise ceiling | same transaction | same |
| Transfer assumption (limitation #1; not a registry row — coverage doc B count is 0) | TRANSFER-FIDUCIAL-01, ~10 runs with a ~500 ms commanded gap | one post-campaign night, but PR #239 is held and the paper itself says the protocol is not runnable |
| The four §3 characterizations (DS-02/03/05/06) | a characterization window (`metrology_v1` pack shape: 40 bundles / 5 levels; 5–10 null blocks × 3 magnitudes; 24 bundles; 6 refs + 3 probes + 3 hold/cool pairs) | NOT in `_v5`; realistically a separate night or two |

### 2.3 Cut for the capstone deadline (keep in the registry, out of the paper)

- The `_v6` GSM8K scored leg (C5-1.9, C5-I.1): post-fiducial, needs its own
  council, and adds a correctness axis the paper does not need.
- The D-163 three-model ladder (model set unresolved under `_v5`).
- All 41 "G" rows; the coverage doc's "three cheapest promotions" (C5-1.6,
  C5-1.12, C5-1.8) each cost measurement nights the sprint does not have.
- Decision for Ed (precomputed): either fold a 5-block identical-condition
  null at ONE magnitude into each floor window (20 members ≈ 40–60 min of
  window time each, and it is the floor's own falsification test per T26 item
  10) or cut §3's four-question table to the one line the campaign supports
  and move the other three to Future work. As written, §3 is the section a PC
  reviewer will read as promising results the paper then cannot show.

---

## 3. PC reviewer: the five most damaging weaknesses, each with the cheapest fix

**W1. The headline rests on an untested transfer, and the test is registered
but not runnable.** All three blind seats (08-28) and the 09-01 Sol seat named
this first. The paper says so plainly (`:1010-1024`), but its own Future Work
now admits the fiducial "is a proposed design, not yet a runnable protocol"
(`:1137-1141`) and PR #239 is titled "HOLD MERGE until _v4 closes" — a
generation that will never be collected. A PC will read: the authors know the
one experiment that would validate the bound, and did not build it.
*Cheapest fix (desk, ~3 h agent time):* re-base #239 onto `_v5`, fix the three
open design elements (sleep actuation = the runtime's existing
`phase_end/prefill` -> `phase_start/decode` seam at `mlx_runtime.py:795-809`;
stamp with the same paired-stamp routine as pulses; fitted edge = falling edge
of the gap and rising edge of decode), and pre-register the residual
comparison rule so the paper can say "registered and runnable, runs the night
after the transaction". Also cite the excursion decomposition's mechanism
paragraph (+13 ms onset bias from dispatch/ramp) as the concrete way transfer
could fail — it is already written in `round7/excursion-decomposition.md`
§"A physical explanation" and absent from §7.

**W2. It is a protocol, not a results paper, and §3 over-promises.** 115 fill
markers; abstract, results, discussion-of-finding, conclusion, references are
build notes. Worse, §3 lays out four characterization questions with
minimum-basis rules (`:303-309`) whose results are all STOP_FILL and which the
`_v5` transaction does not collect (Outcome D). Reviewers forgive "pending" in
a registered report; they do not forgive a Methods section that describes
experiments the paper never runs.
*Cheapest fix (~4 h):* (a) write §6's negative-result subsection now — every
number is MEASURED or ISSUED; (b) cut §3 to the checks the floor windows
actually perform (the floor's own null blocks; bracket band; timing/sampling
flags) and move the rest to Future work with one sentence each; (c) if the
meeting arrives before data, present the paper explicitly as a
pre-registered protocol (registered-report format) — that is a defensible
capstone genre and the advisor is a metrologist who will respect it.

**W3. Statistics: the floor's guarantee is undefined, and inference on ten
blocks from one session is under-defended in the paper body.** The paper
calls the floor "the largest false phase-energy difference allowed by the
fixed calculation" (`:113-114`) but the composition is: max(observed
residual, 95 % prediction amount) -> corner enumeration -> an admittedly
"operational" `g(n)=max(1, sqrt(9/(n-1)))` (`:651-663`, "not a
population-coverage or confidence guarantee") -> plus `A_k`. A reviewer will
ask what probability statement, if any, attaches to `F_cell`; the honest
answer ("none; it is a bound under the enumerated error sources") is not
written anywhere. The dependence problem is handled well in the pre-registered
sheet (`round7/dependence-sensitivity.md`; AR(1) and n_eff halving), but §4
cites it only through an illustrative fixture (`:727-738`) and §7 states the
model constants without the sheet's decision rule.
*Cheapest fix (~2 h):* one paragraph at the end of §4 "What the cell floor
does and does not guarantee" (bound under modelled error sources; not a
coverage interval; `R >= 2` is a pre-registered materiality factor, not a
test), reword "largest false difference this measurement system can
manufacture" to "under the modelled error sources", and state in §7 that the
registered result is reported under all three dependence models with the
most pessimistic direction gate governing the wording.

**W4. Novelty is real but the obvious objection is unanswered: why sample at
100 ms at all?** The whole time-axis argument — the ~30 ms bound, the 37/50
negative, the three-record minimum — is conditioned on a chosen sampler
cadence that the paper never justifies (grep: "100 ms"/"cadence" appear only
in A.3.1 `:1268` and the ledger). `powermetrics` accepts shorter intervals; a
reviewer will ask whether the limitation is the instrument's or the
configuration's, and whether finer sampling perturbs the load
(C-023-TELEMETRY-PERTURBATION is registered as a candidate, not measured).
The excursion decomposition already supplies half the answer: the 13 ms onset
bias is dispatch/ramp latency, which finer sampling would not remove.
*Cheapest fix (~1 h writing, 0 machine time):* a §2 or §7 paragraph stating
the cadence choice, what part of the bound is cadence-driven (record period)
versus not (the repeatable onset bias, the anchor term), and that
sampler-perturbation at finer cadence is untested. If a retained short-interval
capture exists anywhere in `runs_recal*`, cite it; otherwise say so.

**W5. Presentation: the reader-facing text still leaks the process, and the
advisor's vocabulary vanished.** (i) Every omission sentence a reader would
see if unfilled is internal shorthand: "the D-123 reported-mean supplier is not
built (registry row DS-09)" (`:895-906`, the abstract build note `:33-70`).
(ii) "Figure 3 is required here" is reader-facing prose (`:810`), while
`figures/fig3_decision_gates.svg` exists and Figure 4 exists and is never
referenced. (iii) One quantity has four names: `U_edge` (§1 `:115`),
`U_corner` (§4 `:486`), "boundary-moved bound" (§4 heading `:413`),
"corner-widened" (registry, coverage doc); `U_edge` is never used again.
(iv) "detection floor" and "attribution-limited" — the two phrases every
advisor-facing document has used since July (`advisor_briefs/2026-07-30`,
`rivoire-meeting-brief-2026-08-18.md`, README, PROJECT_STATUS) — do not
occur in the v2 body at all; the T26 ruling item 7 required the bridge
sentence "the cell's resolution bound — the artifact calls it the detection
floor". (v) §1 has no scope paragraph (v1 line 27 had it; v2 §1 ends at the
short-prefill question `:149`); the machine is first named in an outcome
sentence template (`:796`). (vi) Length 11.6k + 6.8k appendix against the
ruled 12–16k; §4 alone is ~4,400 words with two synthetic examples and a
fixture.
*Cheapest fix (~3 h):* a "reading copy" renderer that strips build notes and
renders each `[FILL]` as a plain "[not yet measured: <what>]" clause; a
scope paragraph and naming bridge in §1; reference the two existing figures;
assemble §11 from v1 with the 21 cited entries via the existing
`round7/bibliography-renumber-plan.md`.

(Secondary, worth one line each: no external gain check — already limitation
3; C5-1.1 wording is correctly demoted to "demonstration, not scaling";
FLOOR-BIND-01 / "not independently re-reducible" is candid but from outside
reads as "trust us" — say whether it closes before camera-ready.)

---

## 4. Advisor lens: is the metrology story replicable from the text alone?

### 4.1 Replication verdict by section

- **§2 calibration (`:151-197`)** — replicable only via Appendix A.3, which
  is excellent and meets the bar (every constant, refusal name, worked
  capture; a reader can rebuild `B_anchor = 0.0011349971959968978 s` from
  `:1382-1400`). §2 itself names things it does not build and does not
  point to the subsection that does (see 4.2). The bracket constants are now
  derived in text (`:169`) — good.
- **§3 characterization (`:200-364`)** — NOT replicable. Design constants are
  given (40 bundles, 5 levels, 3 magnitudes, 24 bundles, 6 references, 3
  probes) but not the levels, the magnitudes, the cadence ratio, or how the
  comparator `[-m, +m]` is constructed from `floor_train` blocks. A reader
  could not run the ladder.
- **§4 bound and gates (`:397-843`)** — replicable for `U_point`, the corner
  bound, `R`, `R_cm` (fixture with 10-decimal operands), `g(n)`, `A_k`,
  Holm; NOT replicable for `se_metrology` (`:705-717`, sums over unenumerated
  "energy terms") and the decision interval (`:768-772`, "for each named
  kind" of deterministic bound — kinds never enumerated).
- **§5 admission (`:845-875`)** — replicable; thresholds are concrete.

### 4.2 First-use test, run mechanically

Method: strip `<!-- -->` build notes preserving line numbers; for each
candidate term find its first reader-facing line and read whether that
sentence or paragraph builds or glosses it. The shipped ledger (`:1551-1790`,
224 terms, FAILS 0, test passes) is keyed on exact strings, so a singular,
possessive, or compound form escapes it — which is how every row below passed
the test while failing the standard. Terms that FAIL (first use neither built
before nor glossed):

| Line | Term (section) | Why it fails | Cure |
|---|---|---|---|
| 120 | "member's edges" (§1) | "member" defined at `:173` | "each run (member) of a block" |
| 121 | "A/B/B/A block", "shared timing-error sign", "local sign" (§1) | order defined `:173`, formula `:421`; signs built `:588-596` | one clause: "a block is four runs in the order A,B,B,A; a sign says which way a timing error moves every run" |
| 137 | "reasoning disabled" (§1) | Qwen3 thinking mode never explained | "(Qwen3's optional chain-of-thought output is switched off)" |
| 163 | "declared machine state", "the fixed record" (§2) | neither built; the record is the plan's calibration binding | name it: "the frozen plan's calibration entry" |
| 165 | "signal, fit, range … checks", "shared search-work limits" (§2) | defined only in A.3.5 / A.3.7 | add "(Appendix A.3.5, A.3.7)" |
| 167 | "first-record endpoint, stamp brackets, native labels, launch-to-first-parse ordering"; "four separately named allowances" (§2) | constraint names and the four allowances (H, span, r_max, pad) live only at `:1382-1395` | name the four in §2 or point to A.3.3 "Composing the bound" |
| 169 | "calibration policy" (§2) | never built | "the frozen calibration-acceptance rule" |
| 173 | "entry check" (§2) | glossed as "admit a stage" only at `:851` | "(the admission gate of Section 5)" |
| 173 | "reference runs" (§2) | never defined anywhere in the body; §3 `:297` assumes it | "fixed reference workloads repeated at the window's opening, midpoint and close to track drift" |
| 173 | "gross energy", "idle-subtracted energy" (§2) | neither built; idle baseline arrives at `:854` | gloss both in the energy-family sentence |
| 214 | "frozen" (§3) | never glossed in the body | "fixed and fingerprinted before collection" once |
| 236, 307 | "null-test blocks", `null_test`, `floor_train` (§3) | the identical-condition idea is built at `:205-207` but the names are not tied to it; code names leak | "identical-condition (null-test) blocks"; drop the code names |
| 285 | "package power" (§3) | never built | "the summed CPU+GPU+neural-engine power" |
| 292 | "cadence below its fixed ratio" (§3) | ratio never stated | state it |
| 306-307 | "per-token conversion", "workload level", "registered workload magnitude" / "three magnitudes" (§3) | levels and magnitudes never listed | list them or delete the rows (see W2) |
| 370, 382 | "retired calculation", "thirty recorded timing members" (§3) | what was retired (equal-rate anchor? pre-D-165 predicate?) and which window are never said | one sentence: "retired = the equal-rate clock anchor and the guarded predicate that D-165 replaced; members = the 30 phase-absolute runs of the July-25 window" |
| 516 | "close-out records" (§4) | never built | "the post-campaign artifact that checks every ratio" |
| 705 | "energy term" (§4) | `se_metrology` sums over terms never enumerated | enumerate (gross, idle-subtracted, …) |
| 770 | "named kind" of deterministic bound (§4) | kinds never enumerated | enumerate |
| 796 | "named M3 Max hardware" (§4) | machine first named here; §1 has no scope paragraph | scope paragraph in §1 |
| 115 vs 486 | `U_edge` vs `U_corner` (§1/§4) | same quantity, two symbols | one symbol |
| absent | "detection floor" | the advisor's term for two months; bridge sentence ruled (T26 item 7) but not present | one appositive in §1 |
| 810 | "Figure 3 is required here" (§4) | build instruction in reader-facing text | replace with a figure reference |
| 917-940 | "IQR", "record support", "overlap count" (§6) | exist only inside the build note; the ledger claims `built-before` for a section with no prose | write §6 |

Terms that PASS and should be the model: `powermetrics`/sampling record (§1
`:87-91`), phase edge (`:89`), cell / resolution bound (`:112-114`), science
window (`:163`), plateau / resting power (`:165`), monotonic clock (`:167`),
stage / members / block difference (`:173`), clip a record with the 1.20/1.80 J
example (`:404-410`), point-only / unguarded / admitted energy (`:437-445`),
the Student-t prediction amount with worked numbers (`:461-484`), corner
(`:486-492`), the twofold threshold's forcing problem (`:415-419`,
`:508-512`), `not_applicable` absolute `R_cm` (`:636-640`), binary64/ulp
(`:558-576`), Holm with the 0.025/0.05 worked ordering (`:747-756`),
fail-closed (`:847`), nearest-rank p95 (`:854`), and the whole of A.3.2–A.3.7.

Bottom line for the advisor: the calibration can be rebuilt from Appendix A;
the bound and gates can be rebuilt from §4 except two enumerations; the
characterization ladder cannot be rebuilt and is not collected. Twenty-four
first-use defects remain, all cheap, all invisible to the shipped test.

---

## 5. Ranked paper work for the next 20 hours of autonomous agent time

Sizes are agent-hours including the C-028 gauntlet (writer + two refuters +
delta), not machine time. Items 1–6 need no machine window.

| # | Item | Size | Why this rank |
|---|---|---|---|
| 1 | Write §6 "Printed negative result" (`:917-940`) as prose + the record-support diagram, from DG-067..077 (MEASURED) and the issued DG-071/075; flip the two registry rows and the fill-checklist sentences; re-pin R7F. | 3–4 h | The only already-answered RQ gets reader-facing text; every input is on disk; removes one build note the advisor would otherwise read. |
| 2 | Make TRANSFER-FIDUCIAL-01 runnable: re-base #239 on `_v5`, fix the three open design elements named at `:1137-1141`, pre-register the residual rule, update §7 Future work to "registered and runnable". | 3 h | The single largest score lever named by every reviewer seat since 08-28; costs no window now and makes the post-campaign night real. |
| 3 | §1 scope paragraph + naming bridge (resolution bound / detection floor / cell floor; one symbol for `U_corner`; MLX and M3 Max named once) + cure the 24 first-use rows in §4.2; extend the ledger test to singular/possessive/compound forms. | 2–3 h | Cheap; converts the shipped ledger from a string match into the standard. |
| 4 | Pre-write the three outcome branches (A / B / Refusal) for the abstract, §7 "What the finding changes" and §10 as complete paragraphs with numeric `[FILL]` only, plus the Outcome-D prefix. | 3 h | Makes the post-transaction fill mechanical and lets the meeting show the shape of each result even without data. |
| 5 | §3 decision brief for Ed (precomputed: null-block fold-in cost in window minutes vs cut) and, on ruling, either cut §3 to what `_v5` collects or add the null blocks to the alpha/beta packs at the desk. | 1 h brief; 2 h edit | Removes the over-promise (W2) before the advisor reads §3. |
| 6 | §4 "what the floor guarantees" paragraph + the 100 ms cadence paragraph (W3, W4) + cite `anchor-correction-quantified` (2/14 admissibility flips) and Figure 4 in §2/§7. | 2 h | Answers the three most predictable PC objections with material already computed. |
| 7 | Reading-copy renderer: strip build notes, render each `[FILL]` as plain "[not yet measured: …]", assemble §11 from v1 via `bibliography-renumber-plan.md` (21 cited entries), reference fig3/fig4. | 2 h | What Ed actually hands the advisor; no registry IDs on a professor-facing page. |
| 8 | Close the `_v5` desk gaps that make "one window" true: `_v5` extraction spec, final pinset, v2 input manifest in the pack; `RENDERER-V5-SUCCESSOR-01` adapter from close-out to fills. | 4–6 h, parallelizable | Without these the transaction produces bytes the paper cannot consume; belongs in the same 20 h but on Sol seats, not the writer. |
| 9 | Advisor brief refresh (latest is 07-30; the 08-18 meeting brief still says Qwen2.5 / p256): one page — Qwen3 `_v5`, `R >= 2`, dependence sheet, excursion bias, the three questions for her judgment (transfer, Holm family, cadence). | 1 h | The advisor's two-page read currently contradicts the live campaign (09-01 review C6). |
| 10 | Consistency sweep of claim-state surfaces: `CLAIMS_STATUS.md` (last 08-20, cites the retired readiness council), `WINDOW_STATUS.md` (08-24, `_v4`), PROJECT_STATUS phase line, registry rows DG-071/075. | 1 h | Cheap; these are the pages a reviewer opens after the paper. |

Total ≈ 21–24 h; items 1–4 and 6–7 (~15 h) are the paper-critical core.
Not recommended in this window: any new measurement question, the `_v6`
leg, the ladder, or another round of substitution-sheet adjudication (the
09-01 review already ruled "write fresh, do not substitute").
