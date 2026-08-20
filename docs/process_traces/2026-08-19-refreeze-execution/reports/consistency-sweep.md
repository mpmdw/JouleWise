# End-of-block consistency sweep — T12/T12b re-freeze transaction

READ-ONLY sweep. Nothing was edited. Worktree
`/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtS0`,
branch `impl/r2-s0-mint-resolver` @ `246167f` (in sync with origin).

Classification: **(a) MUST-FIX at S6** = a wrong fact a reader would act on ·
**(b) SHOULD-FIX** = stale but harmless · **(c) note-only**.

Headline: the biggest defect is that **the r5→r6 supersession is recorded
nowhere except one parenthetical in `RUN_STATE.md:22`.** Four surfaces — the
D-147 index row, the R2 ruling (its declared ONE HOME), the T12 block, and the
D-145 generation record — all still say r5, while every artifact in the tree
binds r6. Second: `CLAIMS_STATUS.md` never learned that the era barrier became
mechanical, though `docs/paper/draft-v1.md:260` states it correctly.

---

## (a) MUST-FIX at S6

### M1 — README pins a stale, forbidden test count (mechanically proven red)

- **File:line:** `README.md:37`
- **Contradiction:** "The full test suite (3,688 tests) is green at the
  confirmation head." This contradicts README's own policy two paragraphs
  later — `README.md:177-178` ("reader docs intentionally do not copy its
  volatile count") and `README.md:186-187` ("this page does not pin a pass or
  skip count that would drift as coverage grows") — and the number is stale
  (`RUN_STATE.md:30` records 3,755 ran at the S1-clean head).
- **Correct value + source:** remove the literal entirely. This is the *only*
  remaining docs-freshness red, i.e. exactly the residue `RUN_STATE.md:31-32`
  defers to S6. Executed proof:
  `python3 -m unittest tests.test_docs_freshness` →
  `FAIL … AssertionError: [] != [('README', 'suite result count', '3,688 tests')]`
  at `tests/test_docs_freshness.py:187`.
- **Provenance note worth recording:** commit `0418bfc` removed this literal
  under the docs-freshness rule; commit `6f4b553` (T10 docs pass) reintroduced
  it. Second occurrence of the same regression.

### M2 — D-147 index row states the wrong acceptance binding

- **File:line:** `docs/decision_log.md:170`
- **Contradiction:** "immutable `_v3` pack family bound to **r5** AT BIRTH."
  The emitted family binds **r6**.
- **Correct value + source:** `d079_calibration_acceptance_v2_n17_r6`.
  `configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:155`
  (`SUCCESSOR_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n17_r6"`; same in
  the `_7b_v3` and `_contrast_..._v3` generators); `RUN_STATE.md:24`
  ("bound r6 at birth"); commit `1d3873b`.

### M3 — the R2 ruling (D-147's declared ONE HOME) is falsified in four places, with no supersession recorded

- **File:line:** `docs/process_traces/2026-08-19-r1-r2-codesign/14-r2-ruling.md`
  - `:83-91` (S7 "Acceptance binding: **r5** at birth")
  - `:98` (S8 "S3 `_v3` emission ×3 → draft retarget **to r5**")
  - `:103` ("R2's files do not intersect r4/r5's four estimator pins ⇒ **no r6**
    (both seats verified)")
  - `:128` ("the v3 confirmation table Ed is owed will carry **r5**, not r4,
    identities")
- **Contradiction:** all four were overtaken by execution. The S1 fix round 2
  (commit `3038eeb`) edited `joulewise/reduce.py` and
  `joulewise/uncertainty_evidence.py` — two of the four D-138/D-079-pinned
  estimator sources — which forced **D-079 r6** (19-member neutrality proven).
  The `_v3` family binds r6; the confirmation table carries r6.
- **Why MUST-FIX:** `docs/decision_log.md:170` says "ONE home:
  `…/14-r2-ruling.md`. Do not restate the spec here." A reader following the
  authoritative pointer is told r5. `11-r2-debate-terra.md:55` carries the same
  refuted prediction.
- **Correct value + source:** r6 per M2's sources; the falsification is
  commit `3038eeb` (message names the two pins). **The supersession exists
  nowhere in the repo** — the only trace is the parenthetical
  `RUN_STATE.md:22` ("D-079 r5→r6 chain"). Fix shape: an amendment addendum in
  the custody dir (e.g. `15-r5-r6-amendment.md`) recording that S7/S8's
  no-r6 verification was falsified by a fix round, plus an "AMENDED" clause on
  the D-147 index row.

### M4 — D-145 generation record stops at r4; r5 and r6 are unminted

- **File:line:** `docs/decision_log.md:168`
- **Contradiction:** D-145 is the D-079 generation record and covers r3/r4
  only. r5 (commit `b7e5730`) and r6 (commit `3038eeb`) are issued, and **r6 is
  the live artifact** cited as authoritative by `docs/paper/draft-v1.md:52,64,189`
  and `docs/guides/instrument-guide.md:18,403,435`.
- **Correct value + source:** extend D-145 (or mint a successor row) with the
  r5/r6 entries: r5 = flip-forced reissue, three estimator pins; r6 =
  capture-era-presentation reissue, pins `reduce.py` +
  `uncertainty_evidence.py`, 19-member neutrality replay 0 mismatches. Sources:
  `configs/calibration/calibration_acceptance_d079_v2_n17_r{5,6}.json`
  (`derivation_notes.reissue_delta`), commits `b7e5730` / `3038eeb`,
  `docs/process/ed-s5-mint-decision-2026-08-19.md:63-66`.

### M5 — the T12 block still asserts r5 and carries no superseded banner

- **File:line:** `RUN_STATE.md:49-50`, `:65`, `:71`
  - `:49-50` "(2) the `_v3` family binds **r5** AT BIRTH"
  - `:65` "Ed's v3 confirmation table (now carries **r5** identities)"
  - `:71` "the confirmation table basis moves r4 → **r5**"
- **Contradiction:** superseded within the same session by T12b
  (`RUN_STATE.md:24`, `:33-34`) and by the packet's confirmation table
  (`docs/process/ed-s5-mint-decision-2026-08-19.md:63-66`), all r6.
- **Why MUST-FIX:** every other superseded block in the file is banner-marked
  (`RUN_STATE.md:218`, `:307`, `:380`, `:473`, …); T12 is not, so a reader
  scanning down treats it as current detail on the r5 point.
- **Correct value + source:** r6, per M2.

### M6 — CLAIMS_STATUS.md never records the era transition

- **File:line:** `CLAIMS_STATUS.md:21` (Last updated **2026-08-16**, T9 close);
  §2 rows at `:95-96`; §5 at `:173-205`
- **Contradiction:** the file declares itself (`:13-19`) "the single standing
  home for what can we actually claim right now … Refresh this file whenever
  claim-bearing state changes." This session installed a **mechanical** claim
  barrier (D-146 S3/S4): `CLAIM_BEARING_ANCHOR_METHODS = frozenset({CLOCK_METHOD_V3})`
  at `joulewise/uncertainty_evidence.py:1299` with
  `capture_pipeline_refusal()` at `:1322-1324`, wired into
  `analysis_engine/inputs.py`, `floor_extraction.py:191`, `whole_window.py:200`,
  and the new engine reason `capture_pipeline_superseded`. Every stored
  anchor-v2-era bundle (≈748) is now refused at claim admission. CLAIMS_STATUS
  states none of it, and §2 still calls the 7B floors and the 1.5B-vs-7B
  contrast "EVIDENCE-BEARING — collected and verdict-PASSED, awaiting a
  specific gate," naming the blocker as D-117 re-scoping **only**.
- **Correct value + source:** `docs/paper/draft-v1.md:260` already states it
  correctly — "every measurement window collected so far was captured under the
  superseded pipeline, so none of it is claim-bearing under the present
  instrument … the exclusion is now mechanical as well … no retrofit lane
  exists." Also `13-r1-ruling.md` S3/S4/S6 and
  `docs/guides/instrument-guide.md:388-395`. Fix: new dated header entry +
  §2/§5 note that the exclusion is now enforced at admission, not by protocol
  alone.

### M7 — the state kernel arms the wrong pack generation

- **File:line:** `docs/process/state_kernel.json:863`, `:892` (rendered at
  `TASK_QUEUE.md:527`, `:615`; `RUN_STATE.md:3807`; BETA/GAMMA equivalents at
  `TASK_QUEUE.md:528-529`, `:616-617`)
- **Contradiction:** the D117-W-ALPHA/BETA/GAMMA rows name
  `d117_floor_qwen25_1p5b_v1`, `d117_floor_qwen25_7b_v1`,
  `d117_contrast_qwen25_1p5b_vs_7b_v1` as "the frozen pack", and fence on
  "**Exact** frozen pack `d117_floor_qwen25_1p5b_v1` is used". Three
  generations stale.
- **Why MUST-FIX:** `TASK_QUEUE.md:96` makes the generated region "the sole
  live work-selection view"; a cleared council would arm the `_v1` root.
- **Correct value + source:** the `_v2` family is the frozen current one
  (freeze-0002, 2026-08-13/18) and the `_v3` family supersedes it on
  freeze-0003. `ls configs/campaigns/` shows all three generations;
  `RUN_STATE.md:24`, `docs/process/ed-s5-mint-decision-2026-08-19.md:45-51`.

### M8 — kernel `latest_report` and `updated` are two checkpoints behind

- **File:line:** `docs/process/state_kernel.json:22-25` and its `updated`
  field (rendered at `RUN_STATE.md:3803`, `TASK_QUEUE.md:514`)
- **Contradiction:** `latest_report` → `docs/run_reports/2026-08-16-t9-session.md`,
  `updated` → 2026-08-17. `docs/run_reports/2026-08-18-t10-session.md` exists,
  and T11/T12/T12b have happened since.
- **Correct value + source:** the newest run report in `docs/run_reports/`
  (today: the T10 report; ideally a T12 report — see S8) and today's date.

### M9 — WINDOW_STATUS omits the live, dated machine constraint

- **File:line:** `WINDOW_STATUS.md:20-37` (state table `:22-23`; live machine
  rules `:24-30`)
- **Contradiction:** this is the home Ed reads for machine rules, and it does
  not record that 33 arm-readiness evidence receipts now exist at
  `/Users/edr/JouleWise-measurement-20260818`, **expire ~2026-08-20T16:51:33Z,
  and die on ANY reboot** (boot session `da90818c-9c31-45d0-8813-deae65fba143`).
  `WINDOW_STATUS.md:25-26` states only the generic "Do not reboot before T-0";
  there is no T-0, so the rule reads as inactive.
- **Correct value + source:**
  `docs/process/ed-s5-mint-decision-2026-08-19.md:31-36` — "DO NOT REBOOT the
  Mac before ruling"; `RUN_STATE.md:18-19`. Also refresh `WINDOW_STATUS.md:23`
  ("Updated 2026-08-17").

---

## (b) SHOULD-FIX

### S1 — README activity blurb is a full session stale

- **File:line:** `README.md:21-47`
- Header says "last: 2026-08-18 morning" against Ed's standing every-work-block
  refresh rule. Specifics: `:23-25` "Just completed … the entire Phase 2
  successor re-freeze … the three successor packs (the 'v2 family')" now
  describes the *previous* transaction, and a `_v3` family exists; `:41-42`
  "Working on now: … a newcomer-facing instrument guide" — the guide landed
  (`docs/guides/instrument-guide.md`, commit `53e480e`); `:44-47` "Queued next:
  (1) publication of the successor family on explicit confirmation" — the live
  blocker is now the S5 freeze-0003 permission ruling.
- Source: `RUN_STATE.md:15-34`; `docs/process/ed-s5-mint-decision-2026-08-19.md`.

### S2 — README banner names a superseded work program

- **File:line:** `README.md:16-17`
- "Current work is the ten-item U1-U10 instrument-readiness repair path."
  Superseded since 2026-08-15 by the readiness-council repair program
  (Phase-1 code merged → Phase-2 re-freeze → re-audit → READY-candidate council
  → alpha/beta/gamma).
- Source: `RUN_STATE.md:147+` (T9), the `WINDOW-COUNCIL-GATE` at
  `RUN_STATE.md:3788-3796`, `CLAIMS_STATUS.md:28-36`.

### S3 — RUN_STATE "Last updated" names T12, not T12b

- **File:line:** `RUN_STATE.md:13`
- "Last updated: 2026-08-19 (T12 — R1/R2 co-design rulings ratified; re-freeze
  cycle resuming)" while the top block is T12b.
- Correct: T12b — transaction executed through S4; S5 mints blocked on Ed
  (`RUN_STATE.md:15`).

### S4 — both the RUN_STATE pointer and the Ed packet pin a superseded head

- **File:line:** `RUN_STATE.md:21` ("State on impl/r2-s0-mint-resolver @
  `3a75a77` (pushed)") and
  `docs/process/ed-s5-mint-decision-2026-08-19.md:40-41` ("branch
  `impl/r2-s0-mint-resolver` @ `3a75a77`")
- The branch head is `246167f` (`a2f6010` packet → `53e480e` guide/paper →
  `246167f` merge), pushed. The packet instructs Ed to execute the six mint
  commands at `3a75a77`.
- The two later commits are docs-only and change no pack byte, so this is not
  a correctness hazard — but the packet should either name the current head or
  say explicitly that the mint runs at the S4 head and why.

### S5 — WINDOW_STATUS forbids exactly what the S5 procedure requires

- **File:line:** `WINDOW_STATUS.md:26`
- "Do not modify or dirty the dedicated measurement checkout." S4 authored
  **and committed** evidence there, and S5 instructs Ed to run six commands and
  commit each there.
- Source: `docs/process/ed-s5-mint-decision-2026-08-19.md:38-52`,
  `RUN_STATE.md:25-26`. The rule needs a governed-mint / evidence-author
  carve-out.

### S6 — the instrument guide contradicts itself on bind-at-birth

- **File:line:** `docs/guides/instrument-guide.md:595-597` vs `:602-607`
- `:595-597` "Each `_v2` pack's **unedited** generator was run to emit a `_v3`
  tree, and only the emitted, not-yet-frozen drafts were **retargeted at the
  current calibration artifact**" (emit-then-retarget) contradicts `:602-607`
  "**Bind at birth, not by retargeting later** … The successor packs were
  therefore emitted **already bound** to the live generation."
- Correct: bind-at-birth.
  `configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:155`;
  `RUN_STATE.md:24`; commit `1d3873b`. The first sentence reproduces the R2
  ruling's two-step S8 wording (`14-r2-ruling.md:98`), which execution
  replaced — same root cause as M3.

### S7 — the live queue head is not the live work

- **File:line:** `TASK_QUEUE.md:536` / `:629` (A1 `WO-LAUNCH-BINDING`, READY,
  the only READY [AGENT] head)
- The D-147 transaction has **no kernel row at all**:
  `docs/process/state_kernel.json` contains zero occurrences of "D-146",
  "D-147", or "_v3". A fresh session obeying `TASK_QUEUE.md:96` ("sole live
  work-selection view") would start WO-LAUNCH-BINDING instead of finishing
  S5/S6. `RUN_STATE.md:15-34` is currently the only pointer to the real work.

### S8 — no run report for T11 or T12/T12b

- **File:line:** `docs/run_reports/` (newest: `2026-08-18-t10-session.md`)
- `RUN_STATE.md:3752-3756` ("At the end of substantial work … 3. Add or update a
  detailed report in `docs/run_reports/`") is unmet for two checkpoints.
  Custody is split between the RUN_STATE T12/T12b blocks, the codesign trace
  dir, and a **session scratchpad that dies with the session** —
  `RUN_STATE.md:28-29` names `r5-issuance/`, `r6-issuance/`, `s2-goldens/`,
  `s4/` there.

---

## (c) Note-only

### N1 — 3,755 is scoped to the S1-clean head, not HEAD

`RUN_STATE.md:30` ("Canonical at the S1-clean head: 3,755 ran") is honest as
written, but S2-S4 added tests (`tests/test_d117_v3_family.py` +236,
`tests/test_mint_policy_resolver_guard.py`, `tests/test_capture_pipeline_era.py`
+287), so it is not the count at `246167f`. Do not promote it into any reader
doc — that is how M1 happened.

### N2 — D-146 index row's r5 mention is defensible

`docs/decision_log.md:169` ("science-neutral D-079 r5 REQUIRED in the same
commit as the flip") is an accurate record of what the ruling required and what
S1 executed. It misleads only if read as "r5 is live". Covered by the M3/M4
amendment.

### N3 — two correct "not yet minted" notes that expire at S5

`docs/paper/draft-v1.md:189` (trailing comment: "NOTE: freeze-0003 itself is
not yet minted") and `docs/guides/instrument-guide.md:610-613` ("the one step
still outstanding"). Both true today. Add them to the post-mint landing
checklist so they flip the moment Ed rules.

### N4 — cross-checks that PASSED (recorded so S6 need not re-sweep them)

- Generation-id table `docs/guides/instrument-guide.md:429-435` matches the
  artifacts' own `acceptance_id` fields, including the non-obvious
  `…_v2_n19` / `…_v2_n19_r2` (file names are `calibration_acceptance_d079_v2.json`
  / `..._v2_r2.json`, ids are `_n19` / `_n19_r2`). Verified by reading each
  JSON.
- Detection-budget numbers agree three ways: guide `:190-194`
  (115,449 / 122,097 median / 137,535 / 165,000), paper `:52` (max 137,535,
  cap 165,000, ~20%), and r6
  `derivation_notes.derivation_method.corpus_survivor_cell_demand`
  `{n:17, min:115449, median:122097, p95:137535, max:137535}`, budget 165000.
- Era census 745/748 agrees: guide `:392`, paper `:191`, `13-r1-ruling.md` S4.
- 33 receipts / eleven per pack agrees: guide `:609-610`,
  `docs/process/ed-s5-mint-decision-2026-08-19.md:6`, `RUN_STATE.md:25`.
- D-144/D-145/D-146/D-147 body pointers all resolve:
  `docs/process_traces/2026-08-19-r1-r2-codesign/` (14 files),
  `docs/process_traces/2026-08-18-anchor-v3-science-review/`,
  `docs/process_traces/2026-08-18-t10-t11-working-notes/trace-notes.md:423`
  ("## ED PROCESS RULE (2026-08-18 evening): co-design protocol").
- Paper and guide contradict **no** process doc other than via S6; the paper's
  era-transition paragraph (`:260`) is ahead of `CLAIMS_STATUS.md`, which is
  scored against CLAIMS_STATUS (M6), not the paper.

### N5 — historical-region counts are out of scope

`TASK_QUEUE.md:330` ("Canonical replay reached all 3,293 tests") sits in the
superseded/historical region; `tests/test_docs_freshness.py` correctly does not
flag it. Leave as-is.
