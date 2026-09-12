# Counter-review: "When the Benchmark Says No" (prop-refusal-as-result)

Reviewer: Opus 5, counter-review pass. Charge: kill it.
Ground truth: `desk/` @ main, plus a full census of the machine-side run roots.
Every cited number was checked against primary bytes.

**VERDICT: WEAK as proposed** (as a standalone paper). The same material
is STRONG in the two forms named in §Strengthening — neither of which is what
was proposed.

| axis | score |
|---|---:|
| novelty | 3 |
| feasibility | 4 |
| mvp_leverage | 3 |
| venue_fit | 3 |
| original_goals | 3 |

`mvp_leverage` is scored **low deliberately**. See FF5: this proposal's
"leverage" is that it reuses §§1–6 *and* republishes the MVP's results as its own
contribution 4. Leverage that high is not leverage; it is double publication.

---

## What is right (stated first, and it is a lot)

Factually this is the most disciplined proposal I have audited. I tried to break
its numbers and could not:

| claim | status |
|---|---|
| 38 calibration observations; 30 valid / 6 ordinary-invalid / 2 systematic-invalid | **EXACT.** `configs/calibration/calibration_acceptance_d079_v2.json` (`prior_observation_set.observations` = 38; `candidate_inventory` states 30/6/2), independently confirmed against the 76-row physical ledger (38 reservations × 2), head pin `sequence: 76` |
| 229-member early collection arc; four windows non-claim-bearing | **EXACT.** a5=108, a6=19, a7=42, a8=60 → 229 (`README.md:30`, `docs/run_reports/2026-07-23-window-a-collection-arc.md:45-48`); reproduced on disk as 228 live + 1 quarantined; a5/a6/a7/a8 produced 7 FAILED verdicts, zero PASS |
| historical decode contrast ≈ 141.29 J, diagnostic | **EXACT** (`CLAIMS_STATUS.md:63`), and correctly labelled pre-genesis/diagnostic per D-117 |
| pre-genesis 7B comparative-floor diagnostic ≈ 14 J | **EXACT** (13.998036 J, `DESIGN-MEMO.md:271`) |
| 128-token prefill difference ≈ 5.81 J, half-width ≈ 1.81 J, lower edge ≈ 4 J | **EXACT** (ten block deltas 5.645–6.008 J, `2026-08-07-prefill-feasibility/CONSULT-RESPONSE.md:173`; `SYNTHESIS.md:12`) |
| budgets 3.14 / 3.24 / 2.80 h; 140 science bundles; 203 total captures | **EXACT** (`DESIGN-MEMO.md:311-328`; 50+50+40 = 140; +36 bound +21 refs +6 cal = 203) |
| alpha/beta = 10 absolute + 10 A=A ABBA blocks; gamma = 10 blocks | **EXACT** |

The correct ICPE Research-vs-Industry track distinction is also drawn properly,
and the "no quiet window, no borrowed hardware" claim is true.

The problem is not accuracy. **The accurate facts do not add up to the paper.**

---

## Fatal flaws

### FF1 — There is no refusal log. The paper's primary evidence object does not exist as an artifact.

`find` over the entire repo for `refusal*` returns **exactly one file**:
`docs/phase_2/refusal_scope_spec.md` — a 72-line *specification*. Zero committed
machine-emitted refusal records. The phrase "the refusal log" occurs in three
non-derivative places, all prose, two of them in `draft-v1.md` itself (`:17`, `:139`).

The actual evidence is **40 `campaign_log.jsonl` files (1,747 rows) and 1,402
`summary_metrics.json`**, living entirely under gitignored run roots
(`.gitignore:7,25,29,31`) on the measurement machine. None is committed,
published, or hash-manifested into any repo artifact. A paper whose primary
evaluation is "the refusal log" is today proposing to cite ~26k uncommitted files.

The proposal describes this as *converting existing failures* — harvesting. It is
not harvesting. The artifact has to be **built first**, and building it is
contribution 1's exporter plus a custody/publication decision (what raw evidence
may be public) that nobody has made.

### FF2 — The honest denominator is ~6–7 distinct refusal mechanisms, and the proposal never states any denominator at all.

Full census of the machine-side corpus:

| refusal event class | count |
|---|---:|
| whole-window verdicts | 16 (6 PASSED, **10 FAILED**) |
| supersession / quarantine records | 7 |
| member-level `status: failed` rows | 64 (39 `exit_code: 3`) |
| bundles carrying ≥1 precheck reason code | 1,368 |
| refusals in the calibration ledger | **0** |

The 1,368 deflates hard: **24,547 of the 35,019 precheck reason occurrences
(70.1%) are on sub-millisecond `phase/tokenize` and `phase/generation_setup`
windows that refuse BY DESIGN**, documented as such in `refusal_scope_spec.md`.
Those are not incidents; they are a gate working.

And the 10 FAILED verdicts are not 10 stories. a5 ×3 are the *same window* with
largely the same condition set; a6 and a8 are the *same* `neg8_bracket_abs_delta_exceeded`
gate; a8's second is a stale-drift re-verdict of a6/a8's material. Deduplicated by
**distinct refusal mechanism** you have roughly six: environment/admission
missing, NEG-8 corner-statistic exceedance, stale drift bound, GPU-DVFM ramp
aliasing the calibration, clock-anchor unresolved, campaign-membership unresolved.

Six mechanisms, one machine, one operator, one project. That is a strong
**lessons-learned section**. It is not a paper's primary evaluation, and "how
many refusals do you actually have?" is the first question any referee asks. The
proposal answers it nowhere.

### FF3 — The proposal's own kill criterion has already fired, and it does not know.

> "Kill the standalone refusal-paper framing if fewer than 90% of claim-relevant
> refusal outcomes can be reconstructed..."

The desk evidence exists today and points to KILL:

1. **No `{member_id → reason_code}` mapping exists anywhere.** In `campaign_verdict`
   rows the per-member failure is free-text prose — e.g. `"invalid unwaived member
   bundle(s): mtadd-p2048o0128-r08"`. **31 of the 51 distinct condition strings**
   across all campaign logs take this form.
2. **No reason→member join at window level.** In the D-098 verdict record,
   `members` has 68 entries and **0 carry a failed/False field**;
   `idle_admission_core.conditions` is a flat set over the whole window. "Which
   member caused `whole_window_bundle_invalid`?" is answerable only from
   decision-log prose.
3. **The paper's flagship anecdote has no machine record at all.** The single
   refusal `draft-v1.md:139` narrates — the r06 `native_intersection_empty` STOP —
   refused *pre-verdict* and produced **no `campaign_log` row**. Its entire
   existence is markdown in `docs/process_traces/2026-08-03-winB-reeval-stop/`.

The proposal treats the census as future desk work. It is a day's work, it should
be done *before* the direction is funded, and every signal I have says the answer
is below 90%.

### FF4 — Contribution 1 is 100% unbuilt, and there is no single taxonomy to predeclare against.

`grep -rn -i 'fault famil'` across the entire tree: **0 hits.** The phrase does
not exist. `mutation matrix`: 2 hits, both as a *review requirement* in one
2026-08-03 cold-gate thread, never a harness. Parametrized fault tests in
`test_whole_window.py` / `test_reduce.py` / `test_floor_extraction.py`: **0**.
What exists is ad-hoc per-test mutators (`test_envelope_gate.py:61-156`), not a matrix.

Worse than "unbuilt" is what it would have to be built *on*:

- **184 distinct reason codes across 11 disjoint enums** in 5+ modules
  (`claims.py` 97, `floor_extraction.py` 34, `bundle_read.py` 22,
  `detection_floor.py` 15, `calibration_ledger.py` 14, `powermetrics_fiducial.py` 14,
  `whole_window.py` 12, `output_identity.py` 11, `idle_dependence.py` 8,
  `registry.py` 6). There is no ONE home.
- **Only 16 of 184 (8.7%) have ever fired on real data.** 34 appear in neither
  tests nor any bundle — dead vocabulary (`floor_row_stale`,
  `equivalence_not_supported`, `randomization_sensitivity_disagrees`, …).
- **The killer:** the 10 FAILED window verdicts are expressed in a 20-code
  condition vocabulary of which **only 4 appear in any enum**. Sixteen codes —
  `neg8_bracket_abs_delta_exceeded`, `neg8_drift_bound_stale`,
  `whole_window_bundle_invalid`, `cpu_busy_ratio_p95_exceeded`,
  `calibration_identity_change`, … — are scattered literals in
  `idle_admission.py:44-67`, `whole_window.py:95-113`, and bare strings in
  `run_campaign.py:5270,:4921`, and are **not covered by `refusal_scope_spec.md`
  §S1**, the ratified ONE home. *The paper's headline refusal events are governed
  by a shadow taxonomy the project's own spec does not scope.*

A refusal-taxonomy paper cannot ship on a taxonomy that is 91% dead vocabulary
with an unscoped shadow governing exactly the events it wants to publish. And
because the proposal also promises artifact release, a referee gets to *see* the
91%.

### FF5 — Double publication. Contribution 4 is the MVP's results section verbatim.

> "**Contribution 4. Useful science after refusal gates.** Publish fresh 1.5B/7B
> prefill and decode floors plus the prospective decode contrast, each with its
> full decomposition and separate floor-clearance and interval-direction verdicts."

That is `draft-v1.md` §7 (C-v) plus §4 (C-ii). Verbatim. Combined with the
proposal's own admitted reuse of "introduction, background, calibration, floor
composition, protocol, scope, and demonstration methods" (§§1–6), **this is the
MVP paper with a taxonomy table appended.** It is not a second paper.

The concrete risk the proposal never mentions in a §"Venue fit" that discusses
ICPE tracks in detail: CSCSU is a real conference with proceedings. If the
capstone version appears there, an ICPE submission carrying the same §§1–5 text
*and* the same D-117 floors and contrast as its own contribution is a
prior-publication disclosure obligation at minimum, and plausibly a desk reject
under ACM substantial-similarity rules. Method-section reuse across a workshop and
a full paper is normal. Republishing the *same results* as a contribution is not.

### FF6 — The ICPE Research Track argument is right about what the track accepts and wrong about what it takes.

The repo's own venue analysis sets the bar
(`docs/strategy/2026-08-06-impressiveness-roadmap.md`, ICPE full research row):

> "C1–C8, cross-day stability, artifact-ready release, and **at least one deeper
> contribution: held-out Q4 prediction, second-unit replication, or a successful
> mechanism study**." Reported 2026 full-paper acceptance: **28%**.

A refusal taxonomy is none of those three. Nor does it meet what "empirical /
case study" means at that track: those papers have a subject *population*. This
has n=1 project, n=1 machine, n=1 author grading his own tooling on six refusal
mechanisms. The honest ladder is ICPE **Artifact Track** (roadmap rank #3 — and
genuinely strong, because refusals are exactly the thing a reviewer can verify),
ICPE Emerging/WIP at 6 pp, or a workshop. Not full research.

## Non-fatal but recorded

- **Two exact numbers used as a category error.** The 38 calibration observations
  are ruled *dispositions* in a genesis historical import — **not one is a refusal
  record**; the 229 are *collected* members, not refused ones. Contribution 2
  cites both as the refusal corpus. A referee who checks finds the taxonomy's
  empirical base is 10 failed verdicts, not 267 of anything.
- **A hidden adjudication.** The D-079 cold gate initially returned **32
  VERIFIED-VALID / 6 invalid** and was BLOCKED until two of the 32 were re-ruled
  systematic-invalid (`2026-08-06-d079-issuance-coldgate/COLDGATE2-FABLE-transcript.jsonl:11`).
  Quoting "30 valid" without that provenance hides a ruling — a bad look in a
  paper whose thesis is that adjudications must be preserved. Also note the
  *derivation* corpus is n=19, not 38.
- **"Adds no quiet window" is true and irrelevant.** It adds a large desk program:
  unify 184 codes, bring 16 shadow codes under `refusal_scope_spec.md` (and per
  §S4 *every* scope move is a **mandatory cold-gate trigger**, per code), build a
  fault-injection framework, a 184-code coverage matrix, a normalized exporter,
  and deterministic replay. That competes for the exact desk hours D-117's U1–U10
  needs, with three blockers (F1/F2/F3) still open. Ed's priority stack is P1 MVP
  paper, P3 sacrificed if it costs P1/P2. **This is P3 work wearing a P1 badge.**
- Fail-closed-with-preserved-negative-evidence is the stated operating principle of
  MLPerf Power / SPEC (`draft-v1.md:26`, `:182`). The contribution here is a
  well-executed *instance* of a published principle, not a method. That is the
  novelty ceiling, and it is low.

---

## Three strengthening moves

1. **Kill the standalone paper; ship it as the MVP's §5 evaluation plus an ICPE
   Artifact-Track companion.** That is roadmap rank #3, it needs zero extra nights,
   "a reviewer can verify our refusals rather than trust screenshots" is exactly
   the artifact-track product, and it dissolves FF5 entirely — an artifact
   companion to your own paper is expected, not double-dipping. The normalized
   refusal exporter and deterministic replay become the artifact, not a paper's
   contribution 1.

2. **Run the census before funding anything, and publish the denominator.**
   One day of desk work: distinct refusal mechanisms (~6–7), failed windows (10),
   supersessions (7), member failures (64), by-design sub-ms deflation (70.1%),
   and the reconstructability rate. If reconstructability is <90% — and FF3 says
   it is — the proposal's own kill criterion fires and the direction closes
   cheaply. That is the correct next spend regardless of which way it lands.

3. **Fix the defect the census exposed; it is worth more than the paper.**
   Sixteen of the twenty window-verdict condition codes sit outside every enum and
   outside `refusal_scope_spec.md` §S1. Bring the shadow taxonomy under the spec,
   and add a `{member_id → reason_code}` field to `campaign_verdict` rows —
   **before the three D-117 windows run**. Then D-117's refusals are
   machine-attributable *prospectively* instead of prose-reconstructed afterwards.
   That is a real contribution to the MVP's C-iii, it is small, and if it does not
   happen before the nights the evidence is lost for good.
