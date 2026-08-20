# ROW L4 — QUANTITATIVE CLAIM PIPELINE (gating seat, xhigh)

> **Assembler note (read first).** This row is MECHANICALLY ASSEMBLED. No item below is
> graded READY. Where a repair could not be located, the row says so and names what was
> searched.

## HEAD DISCREPANCY — recorded before anything else (material under amendment 12)

Same as ROW-L2; repeated because it conditions every "at the current head" claim below.
Charter amendment 12 (`docs/process/instrument-readiness-audit-charter.md`, §"Verdict form
(amendments 11-12)"): *"final-head invalidation — any repo change after the baseline
manifest voids affected lens results."*

| Source | Head asserted | Verified? |
|---|---|---|
| This assembler's task brief | `4597ad4` | exists: "Preserve prep item 3 (D-144 seat-pass packet) into custody before pause" |
| `ready-packet/_ASSEMBLER-BRIEF.md:12` | `d10881b` | not the tip at read time |
| `ready-packet/raw/CHANGE-UNIVERSE-BRIEF.md:4` | `4597ad4`, 214 commits from baseline | `git rev-list --count 8937dec..4597ad4` = **214** ✓ |
| **ACTUAL `wtS0` tip at assembly time** | **`b92b43d`** ("Shakedown-v3 first-light run card (prep item 6b)…") | `4597ad4` is its **parent** |

**THE HEAD MOVED AGAIN DURING ASSEMBLY OF THIS ROW.** `wtS0` opened at `b92b43d` and
closed at **`7305e0d`** ("Prep sprint: paper staging landed — registry audit (0/34 clean
locators; 8-slot coverage hole; era-codes renderer gap F1), refreshed-registry DRAFT
(anchors only), 5 STOP_FILL figure skeletons + drift-proof generator"). `git rev-list
--count 4597ad4..HEAD` = **2**; `b92b43d` is an ancestor of the new tip, so nothing below
was invalidated by rewrite — but the branch gained commits *while the packet was being
mechanically assembled*. The worktree was never written by this assembler (`git status
--porcelain` empty at close). **A charter-amendment-12 sitting cannot be held against a
branch that is still moving.**

L4's own seat report already flagged amendment 12 for itself
(`seat-reports/L4-quantitative-claim-pipeline-report.md:4`): "the two post-manifest commits
(d279a7c, 8937dec) touch only README.md, RUN_STATE.md, and the manifest itself — **no file
in L4 scope changed after the manifest**, so amendment-12 invalidation does not void this
lens (sitting to confirm)." That reasoning **does not transfer** to the READY-candidate
sitting: 214 commits later, files squarely in L4 scope (`joulewise/reduce.py`,
`joulewise/uncertainty_evidence.py`, `joulewise/whole_window.py`,
`joulewise/analysis_engine/claims.py`, `joulewise/floor_extraction.py`,
`joulewise/calibration_bracketing.py`, and every `configs/floor_mint/` spec) have changed.

## 0. Seat identity and 2026-08-15 result

**Recorded verdict: NOT-READY.** `council-verdict.md:12`: "**NOT-READY. 0 READY / 11
NOT-READY** (ten gating seats + the non-gating L11 basis seat)."

**Seat self-report agrees.** `raw/L4-triage.md:6` (from `triage.json`, seat entry
`L4-quantitative-claim-pipeline`): "seat verdict as reported: **NOT_READY**"; "coverage:
24/27 (evidence_universe_count=27)"; "findings: 4; falsifiers: 4". The seat report closes
(`seat-reports/L4-quantitative-claim-pipeline-report.md:56-58`): "## 8. Verdict:
**NOT-READY** (work orders below) … **finding 1 fires deterministically on ALPHA and BETA
at runbook §11**, and that alone forces NOT-READY for this component."

**No separate UNVERIFIED verdict for L4.** Amendment 11's distinct-verdict split
(`council-verdict.md:13-16`) applies only to **L2**, whose denominator was the one
adversarially tested and fell. **But the council generalised the risk to every seat
including this one** (`council-verdict.md:18-22`, verbatim):

> **The work-order program is NOT CERTIFIED COMPLETE** (Opus B4 cure, cold §E concurring): every seat's evidence universe was self-nominated, and the one denominator adversarially tested fell. Closing all listed work orders does not entitle READY; the READY-candidate re-audit must re-enumerate every universe independently and run the adversarial coverage attack as a standing packet element.

L4's 24/27 denominator was **never adversarially tested**. It is self-nominated
(`seat-reports/L4-…-report.md:7-11`, "Evidence universe (enumerated before findings; 27
items)") and three items are disclosed partial (`:15`).

**No L4 finding was struck.** Disposition 4 (`council-verdict.md:44-45`) strikes L8-B4,
WO-L2-4, and F4's timing premise — none of them L4's. **No L4 finding carries a SINGLE-LENS
label** (Disposition 5, `:46-50`, names only L2-1, L2-COV-1, L2-EDQ-1 and the
terminal-review-trailer producer gap).

**Both refuter lenses confirmed all four L4-cluster findings.**
`refuter-outputs/refuter-verdicts.md:92-99` (ECF-contract, Sol xhigh): "All four CONFIRMED
(L10-B1 consumption edge, **L4-B1 margin recorder**, L9-B1 maintenance census, L9-B2
browser/monitor regexes) … Remedies ruled sound: … **recorder governed-vocabulary
authorization for exactly the plan-tree-pinned spec path**".
`refuter-verdicts.md:101-108` (ECF-execution): "All four CONFIRMED with executed probes: V2
load_manifest refuses v3.prospective schema verbatim; **V3 margin recorder REFUSE
authoritative_input_invalid (forbidden key 'estimator_registration' at pack-pinned
spec.cells[1])** … CLUSTER ECF ADJUDICATED: 4/4 confirmed by both lenses".

---

## 1. FINDINGS — original text verbatim, with citation

Finding IDs are `L4-1`…`L4-4` in the seat report's numbering (BLOCKER 1 / SHOULD-FIX 2 /
SHOULD-FIX 3 / NIT 4); the blocker is referred to as **L4-B1** in the refuter and council
records. The triage extract lists them positionally as F1–F4.

### L4-1 / L4-B1 — severity `blocker`

**Title (verbatim, `raw/L4-triage.md:12`):**
> Margin recorder cannot read the re-specced frozen floor-pack extraction specs — ALPHA/BETA close-out halts deterministically at runbook section 11

**`file_line` (verbatim, `raw/L4-triage.md:13`):**
> `joulewise/window_duration_margins.py:897 (session) + :394 (spec read); cause joulewise/authentication_io.py:179,214; missing authorization mirror of scripts/mint_floor_artifact_generalized.py:1758-1759,3683`

**`failure_scenario` (verbatim, `raw/L4-triage.md:14`):**
> "A funded quiet window collects ALPHA cleanly; the operator runs the exact runbook section-11 command; the recorder opens its V2AuthenticationReadSession and reads the pack-pinned spec, which since the D-133 cl.4 re-spec carries estimator_registration in all comparative cells; the session's reserved-vocabulary rule refuses (executed: REFUSE authoritative_input_invalid, exit 2, no receipt); 'REFUSE stops close-out without writing a receipt' — backup/extraction never run under the mandated order, the window cannot be called claim-bearing, and the standing constraint 'collection close-out gates on the WO-COLLECTION-MARGIN-01 receipt' is unsatisfiable on every attempt. Only the mint authorizes governed-spec vocabulary (allow_governed_extraction_spec); the recorder never does. The committed census tests (tests/test_window_duration_margins.py:213,514) model 'real floor pack cell shapes' WITHOUT the estimator vocabulary, so the suite is green while the real seam is broken — the charter's producer-gap type specimen."

**Citations:** `raw/L4-triage.md:12-14`; seat report §5 BLOCKER 1 (:39-40) and executed
operator-path probe F4 (:35); refuter confirmation `refuter-verdicts.md:93` (contract) and
`:102-104` (execution, executed V3).

**Work order (verbatim, `raw/L4-triage.md:30`):**
> WO-L4-1 (BLOCKER cure): teach joulewise/window_duration_margins.py to authorize governed-spec vocabulary for exactly the one plan-tree-pinned extraction-spec path before its authenticated read (mirror the mint's _allow_governed_extraction_spec single-path pattern; GAMMA analysis-manifest path must NOT be authorized), plus a committed census regression that reads the REAL frozen spec bytes from configs/floor_mint/ (read-only) so the synthetic-fixture/real-vocabulary seam can never silently diverge again; fix the misleadingly named test_census_discovers_all_three_real_floor_pack_cell_shapes to carry estimator/estimator_registration/calibration_basis fields. Full C-028 gauntlet; re-run the three_night_freeze_manifest 'D-133 item (1)' checklist row against frozen bytes, since its assertion was evidently never executed against them.

---

### L4-2 — severity `should_fix`

**Title (verbatim, `raw/L4-triage.md:16`):**
> GAMMA contrast both-gates consumption route is unbuilt: prospective manifest refused by the loader, sole frozen-v3 builder hard-pinned to the splitwise campaign

**`file_line` (verbatim, `raw/L4-triage.md:17`):**
> `joulewise/analysis_manifest_v3.py:34,48,441-447 (ROOT_ORDER_SHA256 splitwise pin, swdec-contrast run-id grammar, 40 entries) vs configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1 (80 rows, d117c15v7-* ids); joulewise/analysis_engine/inputs.py:554-569`

**`failure_scenario` (verbatim, `raw/L4-triage.md:18`):**
> "After a funded GAMMA window, no committed code can produce the frozen v3 analysis manifest the engine requires: load_manifest refuses joulewise.analysis_manifest.v3.prospective (correctly), build_analysis_manifest_v3 refuses the GAMMA order manifest (wrong pinned sha, wrong run-id grammar, 40 vs 80 entries), and zero production code references the d117c15v7 grammar. The funded p256 contrast — the reason the packs re-specced to the 1.869502 J floor — cannot mechanically reach evaluate_claim's both-gates logic; the between-window re-run decision for GAMMA cannot be made on claim outcomes inside the span. Fails closed (no wrong consumption possible), but the missing builder must be registered and its pre-registration binding (prospective contrast census mechanically bound into the built manifest) designed before the GAMMA window."

**Citations:** `raw/L4-triage.md:16-18`; seat report §5 SHOULD-FIX 2 (:42) and executed
probe 6 (:24, "analysis load_manifest refuses joulewise.analysis_manifest.v3.prospective —
executed"); refuter execution lens `refuter-verdicts.md:102` ("V2 load_manifest refuses
v3.prospective schema verbatim").

**Work order (verbatim, `raw/L4-triage.md:32`):**
> WO-L4-2: register and author the D-117 GAMMA frozen-v3 analysis-manifest production path — either generalize build_analysis_manifest_v3 over a pack-declared order/grammar or add a D-117-pinned builder — with the prospective manifest's contrast census (contrast IDs, members, config pins, metric) mechanically bound into the built manifest so pre-registration integrity is enforced by code, not operator discipline; sequence before the GAMMA window or as an explicitly registered post-window dependency with the re-run-decision implication stated.

---

### L4-3 — severity `should_fix`

**Title (verbatim, `raw/L4-triage.md:20`):**
> Margin-receipt consumption never mechanically binds to the FROZEN pack: a repinned truncated pack yields a plausible PASS and the receipt validator accepts a truncated sha-repaired receipt

**`file_line` (verbatim, `raw/L4-triage.md:21`):**
> `joulewise/window_duration_margins.py:988 (validator proves internal consistency only); docs/phase_2/window_runbook.md:1449-1473,1536 (close-out records path+SHA, no pack-binding cross-check)`

**`failure_scenario` (verbatim, `raw/L4-triage.md:22`):**
> "Executed F3-B/F3-C: a pack root whose spec, plan_tree, and sidecar are consistently re-pinned after dropping a comparative cell produces a PASS receipt over the truncated census, and a post-hoc truncated receipt with recomputed cell_inventory_sha256 passes validate_window_duration_margins_receipt. Both leave fingerprints (pack_tree_sha256/registry_source_sha256 differ from the frozen pack), but no close-out step compares them to the frozen pack's committed plan_tree.sha256 — a tired operator pointing --pack-root at a stale draft copy (the registered F-C/F-F CUSTODY_ROOT-ambiguity family makes this realistic) gets a plausible PASS bound to the wrong census, and close-out proceeds."

**Citations:** `raw/L4-triage.md:20-22`; seat report §5 SHOULD-FIX 3 (:44) and executed
falsifier F3 (:33, "**Two attacks succeed structurally**").

**Work order (verbatim, `raw/L4-triage.md:34`):**
> WO-L4-3: add one mechanical close-out check to runbook section 11/12: the reported margin receipt's pack_tree_sha256 must equal the frozen pack's committed plan_tree.sha256 sidecar value (and record that comparison in the section-12 close-out fields); optionally have the recorder CLI print the plan-tree sha it bound so the check is a single diff.

---

### L4-4 — severity `nit`

**Title (verbatim, `raw/L4-triage.md:24`):**
> validate_floor_artifact's recomputation tolerance accepts a one-ULP-understated floor; tamper-evidence rides on byte custody, not numeric revalidation

**`file_line` (verbatim, `raw/L4-triage.md:25`):**
> `joulewise/detection_floor.py:2021 (_close, min(~1e-12 relative, 1e-6)); enforcing layers scripts/mint_floor_artifact_generalized.py:2484-2490 (exact Decimal) and joulewise/analysis_engine/artifact.py:943 (file_sha256 binding)`

**`failure_scenario` (verbatim, `raw/L4-triage.md:26`):**
> "Executed: a one-ULP downward perturbation of the committed mint1 artifact's comparative floor passes validate_floor_artifact with zero errors. Not exploitable end-to-end today because the mint's postcollection/binding equalities are exact-Decimal (refused all my floor-value ULP attacks) and every claim-side consumption re-authenticates artifact bytes against a bound sha256 — but nobody should ever cite validate_floor_artifact alone as tamper-proofing, and any future consumption path that skips the sha binding would inherit a ~1.9e-12 J silent understatement window."

**Citations:** `raw/L4-triage.md:24-26`; seat report §5 NIT 4 (:46) and executed contrast
probe inside F2 (:31).

**Work order (verbatim, `raw/L4-triage.md:36`):**
> WO-L4-4 (record-only): document that validate_floor_artifact numeric revalidation is defense-in-depth behind byte custody (one-ULP understatements pass _close); any new floor-artifact consumption path must bind file_sha256 like analysis_engine/artifact.py:943 or use the mint's exact-Decimal equality.

---

## 2. WHAT CHANGED SINCE 2026-08-15

### 2.a L4-1 / L4-B1 — WO-MARGIN-RECORDER-AUTHZ: **cure LANDED and MERGED**

- **PR #151**, merge commit **`00ec3b7`** — "WO-MARGIN-RECORDER-AUTHZ: narrow
  governed-vocabulary grant for the plan-tree-pinned floor spec (#151)" (verified by
  `git log --oneline -1 00ec3b7`).
- **WHERE it lives: merged to main.** `00ec3b7` is an ancestor of `origin/main`
  (`0099382`) and of the branch head.
- **TASK_QUEUE line 105** (Completed Queue Items table), verbatim evidence text: "Merged
  via #151 (`00ec3b7`): close-out blocker L4-B1 cured under the adopted narrow-grant
  contract; the check-to-grant race remains a REGISTERED LIMITATION with
  WO-RECORDER-GRANT-IDENTITY queued for its own rule-11 gate."
- **T8 run report** (`docs/run_reports/2026-08-15-t8-session.md:152`), verbatim: "**MERGED
  #151** `00ec3b7`, 22:52:17Z | **Close-out blocker L4-B1 CURED** — the recorder now PASSes
  on the re-specced frozen pack. The **check-to-grant race is a REGISTERED LIMITATION**,
  not a claimed closure; **WO-RECORDER-GRANT-IDENTITY queued for its own rule-11 gate.**
  D-121: head `10488ca` == terminal-delta ACCEPT-FOR-MERGE head; CI green (a known
  FLAKE-CALEXITS-class 3.14 failure cleared on rerun, module untouched by the diff). 2
  files, +453/−92."
- **Code verified at the current head**, `joulewise/window_duration_margins.py:407-434`:
  the grant is `authentication.allow_governed_extraction_spec(registry_path)` at **:428**,
  preceded by a resolution-invariance guard whose comment reads "The grant must bind the
  literal committed file: the selected path must be resolution-invariant (no symlinked
  component anywhere from the repository root down), so an in-repo alias can never retarget
  the governed-vocabulary grant to a different pack's spec (adoption clause 1: never
  granted the other floor pack's spec)." Symlinked-component detection refuses with
  `authoritative_input_invalid`.
- **WO-L4-1's "GAMMA analysis-manifest path must NOT be authorized" constraint holds at the
  current head.** The GAMMA branch is structurally separate: `analysis_path =
  downstream.get("analysis_manifest_path")` (:393) with a mutual-exclusion check
  (`floor_pack_selected == gamma_pack_selected` → refuse, :396), and the GAMMA read at
  :462-487 (`label="pack-pinned GAMMA analysis manifest"`) **never calls**
  `allow_governed_extraction_spec`. Verified by grep — the only call site in the file is
  :428.
- **Cold-gate record for the residual race:**
  `docs/process_traces/2026-08-15-recorder-race-coldgate/` (packet `8b6c872`, adjudicator
  ruling `8c7843a`, composed verdict `5cdec0c`), plus
  `docs/process_traces/2026-08-16-grant-identity-consult/` (`README.md`,
  `consult-prompt.md`, `consult.md`).

### 2.b The registered check-to-grant limitation, and WO-RECORDER-GRANT-IDENTITY's **RETIREMENT WITHOUT IMPLEMENTATION**

- **TASK_QUEUE line 102**, verbatim: "| WO-RECORDER-GRANT-IDENTITY | P2 Next Slice |
  2026-08-17 | Key the governed extraction grant to a verified identity (recorder
  check-to-grant race cure) | **RETIRED WITHOUT IMPLEMENTATION by D-139 A1** (Ed:
  in-process adversary out of model) — the registered check-to-grant limitation stands as
  the permanent disposition; design consult custodied
  `docs/process_traces/2026-08-16-grant-identity-consult/` should appetite change. |"
  Note it sits in the **Completed Queue Items** table despite never being implemented.
- **D-139 A1 body**, `docs/decision_log.md:10047-10058`, verbatim: "**A1 — In-process
  adversary RULED OUT OF MODEL (registered limitation, family-wide).** Ed: 'no adversarial
  programs affecting the measurement can be assumed.' Consequences, effective immediately:
  (1) WO-RECORDER-GRANT-IDENTITY is RETIRED to the registered check-to-grant limitation —
  no implementation, no cold gate (the design consult remains custodied at
  docs/process_traces/2026-08-16-grant-identity-consult/ should the appetite ever change);
  (2) the T-0 trusted-operator limitation v1 is FINAL for the MVP claim (option-(a)
  attested capture stays closed); (3) the launch-binding forged-complete-context residual
  is FINAL as registered. **The paper states the assumption once, plainly.**"
- **D-148 clause (6)** re-affirms it (`docs/decision_log.md:171`): "the risk-appetite family
  (recorder race / T-0 capture provenance / hostile same-UID injection / forged
  launch-context) is ACCEPTED AS REGISTERED LIMITATIONS — in-process adversary out of
  model, per D-139 A1."
- **The limitation's technical statement** is at `docs/decision_log.md:9519`:
  "(window_duration_margins.py) is subject to a check-to-grant TOCTOU: a concurrent local
  process…".
- **Registration gap worth the seat's attention:** the limitation is **NOT in
  `docs/risk_register.md`**. `grep -rn "check-to-grant\|check_to_grant" docs/` returns hits
  only in `council_log.md`, `decision_log.md`, two run reports, and the two consult/cold-gate
  trace dirs. The risk register's newest rows are R-019 and R-020 (both D-141 residuals);
  no recorder-race row exists. Registration therefore rests on the decision log + a
  Completed-Queue evidence cell.

### 2.c L4-2 — **NO REPAIR FOUND at the current head**

Verified in `wtS0` at the tip:

- **Zero production references to the GAMMA run-id grammar.**
  `grep -rn "d117c15v7" --include="*.py" joulewise scripts` → **no matches** (the exact
  condition the finding named: "zero production code references the d117c15v7 grammar").
- `joulewise/analysis_manifest_v3.py` still carries the splitwise pin and grammar unchanged:
  `ROOT_ORDER_SHA256 = (` at **:48**; `RUN_ID_RE = re.compile(` at **:62** with pattern
  `r"^swdec-contrast-b(?P<block>[0-9]{2})-(?P<position>a1|b1|b2|a2)$"` at **:63**; enforced
  at :420, :522, :534, :610, :814, :877.
- **No WO-L4-2 row exists** anywhere in `TASK_QUEUE.md`. `grep -n "WO-L4-"` over the whole
  file returns **only** the WO-MARGIN-RECORDER-AUTHZ Completed row at line 105 — i.e. of
  the four L4 work orders, **only the blocker cure was ever registered as a queue row**.
- **Searched:** `grep -rn "d117c15v7"` across `joulewise/` and `scripts/`; `grep -n
  "ROOT_ORDER_SHA256\|swdec-contrast\|RUN_ID"` in `analysis_manifest_v3.py`; `grep -n
  "WO-L4-\|L4-B1\|GAMMA.*manifest\|WO-GAMMA"` in `TASK_QUEUE.md`; the Completed Queue table.
- **The GAMMA pack family has since tripled**, which enlarges rather than closes the gap:
  `configs/campaigns/` now holds `d117_contrast_qwen25_1p5b_vs_7b_{v1,v2,v3}` (plus the two
  floor families ×3). The finding was written against `_v1`.

### 2.d L4-3 — **NO REPAIR FOUND at the current head**

- `grep -n "plan_tree.sha256\|plan_tree\.json.*sha\|receipt.*pack_tree" docs/phase_2/window_runbook.md`
  → **no matches**. The only `pack_tree_sha256` hits in the runbook (:315, :319, :821-822)
  are the *definition* of `joulewise.committed_pack_tree_sha256.v1` and a helper snippet —
  **not** a close-out comparison against the frozen pack's committed `plan_tree.sha256`.
- No §12 close-out field recording the comparison was located.
- **No WO-L4-3 queue row exists** (same grep as §2.c).
- The **D-133 item (1)** checklist row that WO-L4-1 ordered re-executed against frozen bytes
  is at `docs/phase_2/three_night_freeze_manifest.md:170` and is still an **unchecked
  `- [ ]`**. Its text confirms the close-out contract as written: "After collection, generate
  the receipt immediately after the finalized post-calibration slot and before backup or
  extraction; **record its path and SHA-256 at close-out**" — i.e. path + SHA only, exactly
  the gap L4-3 named. **No pack-binding cross-check was added to it.**

### 2.e L4-4 — **NO REPAIR FOUND** (record-only work order)

`WO-L4-4` is record-only: document the `_close`-tolerance / byte-custody posture. **No
queue row and no located documentation change.** Searched: `TASK_QUEUE.md` for `WO-L4-`;
the Completed Queue table. The seat should note that the *substantive* posture L4-4
describes (enforcement rides on the mint's exact-Decimal gates + claim-side `file_sha256`
binding) was verified sound by the seat's own executed F2 — the owed artefact is a written
record, not a code change.

### 2.f The claim barrier — D-146, commit `b7e5730` (new consumption fence, post-council)

- **D-146** (`docs/decision_log.md:169`), verbatim: "R1 RULING — PRODUCTION
  CAPTURE-PIPELINE V3 ADOPTION (magistrate, 2026-08-19, under D-144): p2-038.3
  schema+method identity with single-key dispatch and `clock_anchor_era_inconsistent`
  cross-check; **eras retained forever**; era-faithful strict verify (the cli.py:1575
  rich-telemetry fail-open is a blocker fixed in the flip commit); **ONE shared claim-barrier
  predicate (`CLAIM_BEARING_ANCHOR_METHODS`) with NEW engine reason
  `capture_pipeline_superseded`**; no era-stamping on controller fallback evidence; ratified
  union site census incl. `arm_readiness.py` issued-set; science-neutral D-079 r5 REQUIRED
  in the same commit as the flip. ONE home:
  `docs/process_traces/2026-08-19-r1-r2-codesign/13-r1-ruling.md`."
- **Landing commit `b7e5730`** — "S1: anchor-v3 production flip + D-079 r5 (science-neutral,
  19-member replay proven) + claim barrier (D-146)".
- **WHERE it lives: BRANCH-ONLY.** `origin/main` is `0099382` ("RUN_STATE: T12 pointer —
  active successor order lives on impl/r2-s0-mint-resolver"); the S0–S5 chain is not on main.
- **Code verified at the current head** — the barrier reaches directly into L4's scope:
  - `joulewise/uncertainty_evidence.py:1299` `CLAIM_BEARING_ANCHOR_METHODS =
    frozenset({CLOCK_METHOD_V3})`; :1322-1324 returns `"capture_pipeline_superseded"` for
    any other method.
  - `joulewise/analysis_engine/claims.py:136` and `:174` — the reason is wired into the
    **five-outcome claim precedence** (L4 evidence item 9).
  - `joulewise/whole_window.py:200` (L4 evidence item 14),
    `joulewise/floor_extraction.py:191` (item 3),
    `joulewise/calibration_bracketing.py:1280,2123,2128`.
- **D-148 clause (7)** (`docs/decision_log.md:171`): "the stored anchor-v2 population (748
  repo-tree bundles) gets a REGISTERED LIMITATION paragraph: permanently non-claim-bearing
  on estimator grounds, **mechanically enforced by the D-146 barrier**." This is a new,
  post-council, claim-side fence whose correctness is squarely L4's charter and which **no
  seat has audited**.

### 2.g Capture-era system, r6 acceptance, and the D-079 r5→r6 supersession

- **Capture eras:** D-146 installs "p2-038.3 schema+method identity with single-key dispatch
  and `clock_anchor_era_inconsistent` cross-check; eras retained forever; era-faithful strict
  verify". The era pre-filter and per-lane barrier pins land across the S1 fix rounds
  (`1ec5dc4` "era fixture repairs", `3038eeb` "allowlist era pre-filter", `d279bd2`
  "live-three-window scenario converted to anchor-v3 (missed census site); v2 pre-filter
  refusal arm retained", `6f00d05` "thermal-handoff v3 isolation").
- **r6 supersedes r5** — ruling document
  `docs/process_traces/2026-08-19-r1-r2-codesign/15-amendment-r6.md`, verbatim opening:
  "# AMENDMENT (2026-08-19, magistrate) — r6 supersedes r5 as the family's bound generation".
  Its mechanism, verbatim: "That verification was TRUE OF THE DESIGN and FALSIFIED BY A FIX
  ROUND: S1 fix round 2 (commit 3038eeb), executing the two-lens blocker verdict (BLOCKER-2
  predicate inversion; the S3 taxonomy split), edited `joulewise/uncertainty_evidence.py` and
  `joulewise/reduce.py` — two of the four D-079-pinned estimator sources — and therefore
  forced the science-neutral r6 reissue in the same commit (19-member replay, zero
  mismatches; custody in the session scratchpad `r6-issuance/`, digest `0227bca3…`)."
  Amended readings: "S7: the `_v3` family binds **r6** at birth (executed:
  `configs/campaigns/d117_*_v3/generate_configs.py` SUCCESSOR_ACCEPTANCE_ID =
  `d079_calibration_acceptance_v2_n17_r6`)"; and "**r5 remains registered, byte-identical
  history — exactly as r3/r4.**"
- **Both generations are live in the tree at the current head** (this is by design under
  "eras retained forever", not necessarily staleness — the seat must decide which):
  `configs/calibration/calibration_acceptance_d079_v2_n17_r5.json` **and** `…_n17_r6.json`
  both exist; `joulewise/calibration_bracketing.py` references **r5 ×3 and r6 ×3**;
  `joulewise/arm_readiness.py` references **r5 ×1 and r6 ×1**;
  `scripts/floor_mint_pinsets/schema_v2.json` references **r5 ×1 and r6 ×1**. The `_v3`
  packs and `_v3` extraction specs are **r6-only** (12 r6 references in each of
  `configs/floor_mint/d117_qwen25_{1p5b,7b}_v3_extraction_spec.json`).
- **D-147** (`docs/decision_log.md:170`) — R2 mint-lane ruling: "generation-indexed
  mint-policy resolver (registry-authoritative, operatives-crosswire refusal) PLUS immutable
  `_v3` pack family bound at birth to the LIVE generation (r5 per the ruling as written; **r6
  in execution** — fix-round pin moves forced the r6 reissue…); `_v2` packs READ-ONLY
  including their generators (frozen pack content); freeze-0003 chained to freeze-0002…;
  binding sequencing S0-S6 with freeze-0003 as the last acceptance-bearing step."
- **The S0–S5 mint-lane commits on the branch** (verified by `git log`):
  `cef3306` (S0 kernel: generation-resolved mint policy, genesis digest rename, schema
  generation conditionals) · `6771924` (S0 regressions) · `8018a4b` (S0 fix round 1) ·
  `b7e5730` (S1 + D-146 barrier + r5) · `1ec5dc4` (S1 fix round) · `3038eeb` (S1 fix round 2
  — **forced r6**) · `d279bd2` (S1 fix 3) · `6f00d05` (S1 fix 4) · `d8f1202` (S2: r6 golden
  re-derivation via independent fixture oracle) · `1d3873b` (S3: `_v3` pack family emitted
  via unedited `_v2` generators, bound to r6 at birth) · `8b2b021` (S5 COMPLETE: confirmation
  table filled — three freeze-0003 receipts + committed tree digests). Freeze-0003 family
  commits per the assembler brief: `5e38f1e` (1p5b_v3), `eb7f6c6` (7b_v3), `94dc3b3`
  (contrast_v3).
- **Net effect on L4's evidence universe:** items 17–21 of the seat's 27-item universe were
  the `_v1` frozen specs and packs. There are now **three generations** of each
  (`configs/floor_mint/` holds `d117_qwen25_{1p5b,7b}_extraction_spec.json`,
  `…_v2_extraction_spec.json`, `…_v3_extraction_spec.json`; `configs/campaigns/` holds
  `d117_{floor_qwen25_1p5b,floor_qwen25_7b,contrast_qwen25_1p5b_vs_7b}_{v1,v2,v3}`). The
  seat's baseline verification ("pack digests, spec pins, sidecars, acceptance sha — all
  verified against the manifest", report :23) covers the `_v1` generation only.

### 2.h The 165k detection budget — D-143 / D-138 (upstream of every L4 number)

- **D-143** (`docs/decision_log.md:166`), verbatim: "DETECTION-PROJECTION CELL BUDGET
  100,000 → 165,000 (magistrate parameter ruling, 2026-08-18; license records:
  `docs/process_traces/2026-08-18-shakedown-first-light/` 02+03): the maiden live capture and
  three issued corpus members all exhaust 100k under the budgeted detector (real workload
  112,205–137,189 cells, n=34 complete-corpus sweep); 165,000 = max + 20.3% headroom,
  exceeding the whole observed spread; fail-closed semantics retained; behavioural kill tests
  pin the production path. D-138 cycle re-executed in full (one-pin reissue in place, packs,
  evidence, freeze-0002 re-mints at the measurement checkout); first-light re-derivation
  IN-BAND (b_fiducial 0.030878 s ∈ [0.022741, 0.033559])."
- **D-138** (`docs/decision_log.md:163`) is the mechanism by which any such change reaches
  L4's frozen artefacts, verbatim: "any change to the four governed estimator inputs
  (`joulewise/powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py`,
  `reduce.py`) stages on the Phase-2 transaction branch and lands only inside the ONE atomic
  successor-family re-freeze that folds the D-079 acceptance re-issue."
- **Code verified at the current head:** `joulewise/powermetrics_fiducial.py:88`
  `DETECTION_PROJECTION_CELL_BUDGET = 165_000`, :92 `DETECTION_PROJECTION_WALL_BUDGET_S =
  120.0`. **Also on `origin/main`** (:87 / :91 there).
- **Why this is an L4 row and not only an L2 row:** `reduce.py` and `uncertainty_evidence.py`
  are L4 evidence items (1 and, transitively, the whole-window basis at item 14), and
  D-138's coupling is the reason the r5→r6 reissue happened at all. Every floor number the
  seat re-derived (notably the registered **1.8695016260131627 J**, report :20) sits
  downstream of the detector this budget governs.

---

## 3. ED-QUALIFICATION ROWS

### ED-QUAL-L4-1 — decisive replay (network capability)

**Verbatim row text (`raw/L4-triage.md:40`):**
> ED-QUAL-L4-1 (network capability, not hardware/sudo — emitted so it is not silently skipped): execute scripts/replay_d117_decisive.sh at the audited head in any tap block with network — anonymous release download, digest gate, governed hydration, census byte-compare, then the single decisive no-skip mint test (~3h35m on the M3 Max). Stable evidence; closes the two skipped decisive tests and the full-fixture leg of the mint's exact-equality proof.

**LOCATED CLOSURE EVIDENCE — executed and recorded PASS, with a head caveat.**

`docs/run_reports/2026-08-18-t10-session.md:108`, verbatim row from the Ed-qualification
table (custody root `~/JouleWise-window-custody/ed-qual-20260817/`):

> | **ED-QUAL-L4-1 decisive replay** | **`DECISIVE REPLAY: OK`** — full chain (download, digest, hydration, census byte-compare, decisive no-skip mint), 23 proof selections, **13,180.653 s** total | `decisive-replay.log` |

13,180.653 s ≈ 3 h 40 m, consistent with the row's ~3h35m estimate. All five named legs of
the row were executed.

**Corroborating artefacts located:**
- `scripts/replay_d117_decisive.sh` exists and is executable (2,143 bytes, tracked).
- The downloaded custody-store asset is present in the **main checkout's untracked**
  `.decisive-replay/` directory: `/Users/edr/code/JouleWise/.decisive-replay/d117_v2_production_custody_store.tar.zst`,
  40,386,363 bytes, mtime **2026-08-17 17:44** — i.e. the download leg's artefact, dated the
  day before the successful run.

**Three qualifications the seat must weigh, all from the repo's own record:**

1. **Wrong head.** The row demands execution "**at the audited head**" (= baseline `8937dec`
   / manifest head `ac3fe1d`). The run is dated 2026-08-18, ~3 days and hundreds of commits
   later, and one of its three attempts *failed because of drift in the decisive test itself*
   — see (2). The evidence file `decisive-replay.log` lives under the **external** custody
   root `~/JouleWise-window-custody/ed-qual-20260817/`, not in the repo; **this assembler did
   not read it** (outside the read-only worktree and not enumerated in the task inputs).
   No head pin for the run was located.
2. **It took three attempts, and two of the failures were real defects — one of them in the
   decisive test itself.** `docs/run_reports/2026-08-18-t10-session.md:112-113`: "The
   decisive replay took **three attempts**: attempt 1 died on a stale work-dir default,
   attempt 2 on the decisive-test drift, attempt 3 clean. **Both aborts were themselves
   qualification catches** — the layer paid for itself twice before it produced its verdict."
   The curing commits (`:118-127`, "All four commits verified present on `main` and on the
   transaction branch"):
   - **`724ea28`** — "**Decisive-test drift**: `mint1.STACK_IDENTITY_DOMAIN` was removed by
     #131 and re-introduced stale by the `add914a` resynthesis; the decisive leg is
     CI-excluded, so **only the operator replay could hit it**."
   - **`1500265`** — "`replay_d117_decisive.sh` defaulted its work dir **inside the repo**,
     self-refusing against the hardened hydrator → explicit external dir now required; plus a
     **sub-second AST guard test** (`tests/test_decisive_reference_resolution.py`) so the
     decisive-test reference drift is caught by fast CI."
   Consequence for the seat: **the PASS was produced against a script and a test that were
   both patched during the qualification session** — so the artefact proved is not byte-wise
   the artefact the row named at the audited head.
3. **The row's stated purpose was to close two specific skips.** Verbatim: "closes the two
   skipped decisive tests and the full-fixture leg of the mint's exact-equality proof" —
   i.e. `test_coordinated_report_and_pin_change_refuses_against_floor_evidence` and the
   split-partition test (`raw/L4-triage.md:46`). **No artefact was located showing those two
   named tests now run un-skipped in the ordinary suite at the current head.** Searched:
   `grep -rn "replay_d117_decisive\|decisive replay\|ED-QUAL-L4-1\|decisive-replay"` across
   `docs/`, `RUN_STATE.md`, `TASK_QUEUE.md`.

**Note on the other two seats' ED rows referenced in the council program**
(`council-verdict.md:89-95`): EDQ-L2-1 and EDQ-L2-2 are adjudicated in `ROW-L2.md`, not here.

---

## 4. CANDIDATE DISPOSITIONS FOR THE SEAT TO ADJUDICATE

**Candidate dispositions are assembled, not adjudicated; the seat rules.**

| Item | Candidate disposition | What is attached / what remains |
|---|---|---|
| **NOT-READY verdict (machine)** | STILL-OPEN | The blocker that "alone forces NOT-READY" is cured and merged; three should-fix/nit rows and the un-tested coverage denominator remain. |
| **L4-1 / L4-B1** (blocker) | **READY-EVIDENCE-ATTACHED** | PR **#151** / `00ec3b7`, merged to main, TASK_QUEUE:105; grant at `window_duration_margins.py:428` behind a resolution-invariance guard; GAMMA path structurally excluded (verified: single call site). Remaining for the seat: (a) the committed regression binds the **`_v1`-generation** spec path — see probe P1; (b) the WO's ordered re-execution of the **D-133 item (1)** freeze-manifest row against frozen bytes is **still an unchecked `- [ ]`** at `three_night_freeze_manifest.md:170`; (c) the check-to-grant residual is accepted, not closed. |
| **check-to-grant limitation / WO-RECORDER-GRANT-IDENTITY** | **SUPERSEDED-BY-RULING — retired without implementation** | D-139 A1 (`decision_log.md:10047-10058`), re-affirmed by D-148 cl.(6); TASK_QUEUE:102 places it in **Completed** with the evidence cell "RETIRED WITHOUT IMPLEMENTATION". Design consult preserved at `2026-08-16-grant-identity-consult/`; cold gate at `2026-08-15-recorder-race-coldgate/`. Remaining: it is **not in `docs/risk_register.md`**, and D-139 A1 requires "The paper states the assumption once, plainly" — no paper text was located. |
| **L4-2** (should_fix, GAMMA builder) | **STILL-OPEN — NO-REPAIR-FOUND** | Zero production references to `d117c15v7`; `ROOT_ORDER_SHA256` and the `swdec-contrast` grammar unchanged at `analysis_manifest_v3.py:48,62-63`; **no WO-L4-2 queue row exists**. The pack family has since tripled to `_v1/_v2/_v3`, enlarging the gap. Fails closed, so no wrong consumption is possible — but the funded p256 contrast still cannot mechanically reach `evaluate_claim`. |
| **L4-3** (should_fix, receipt↔frozen-pack binding) | **STILL-OPEN — NO-REPAIR-FOUND** | No `plan_tree.sha256` comparison anywhere in `window_runbook.md`; the D-133 item (1) row still specifies "record its path and SHA-256 at close-out" only; **no WO-L4-3 queue row exists**. The two structurally-succeeding attacks (F3-B repinned truncated pack → PASS; F3-C sha-repaired truncated receipt → validator accepts) are unaddressed. |
| **L4-4** (nit, record-only) | **STILL-OPEN — NO-REPAIR-FOUND** | No queue row, no located documentation change. The substantive posture is sound per the seat's own executed F2; the owed artefact is the written record. |
| **ED-QUAL-L4-1** | **ED-ROW — closed-with-evidence, AT A LATER HEAD AND VIA A PATCHED SCRIPT** | `DECISIVE REPLAY: OK`, 23 proof selections, 13,180.653 s (`decisive-replay.log`, external custody root, **not read by this assembler**). Caveats: row says "at the audited head", run was 2026-08-18; three attempts, two aborts curing real defects including **decisive-test drift `724ea28`** and the **replay-script work-dir defect `1500265`**; the two named skipped tests were not shown running un-skipped at the current head. |
| **Coverage 24/27 (never adversarially tested)** | **STILL-OPEN as a standing packet element** | `council-verdict.md:20-22` makes independent re-enumeration + the adversarial coverage attack mandatory for **every** universe at the READY-candidate sitting, precisely because self-nominated denominators proved unreliable. L4's universe is self-nominated, three items are disclosed partial, and it has grown materially (three pack generations, three spec generations, the D-146 barrier, era machinery). **No L4 re-enumeration at the current head exists.** |

---

## 5. WHAT A SKEPTICAL SEAT SHOULD PROBE

All commands assume `cd <wtS0>`; all are read-only.

**P1 (MANDATORY — can claim-consuming code still reach unverified numbers? The `_v1`/`_v3`
regression seam).** WO-L4-1 demanded "a committed census regression that reads the REAL
frozen spec bytes from `configs/floor_mint/` (read-only) **so the synthetic-fixture/
real-vocabulary seam can never silently diverge again**". At the current head the regression
resolves:
```
sed -n '91,102p' tests/test_window_duration_margins.py     # _floor_spec_path
grep -n "d117_floor_qwen25" tests/test_window_duration_margins.py
```
`_floor_spec_path` builds `configs/floor_mint/d117_qwen25_{model}_extraction_spec.json` — the
**unsuffixed `_v1`-generation** spec — and the pack constants at :43 and :54 are
`d117_floor_qwen25_1p5b_v1` / `d117_floor_qwen25_7b_v1`. But the live claim-bearing family is
now `_v3` (r6-bound), and `configs/floor_mint/` holds `_v2` and `_v3` specs too.
*Falsifier:* if a `_v3`-generation regression exists elsewhere (search all of `tests/` for
`_v3_extraction_spec`), the seam is covered and this probe fails. If not, **the exact
producer-gap the blocker cure was built to prevent has reopened one generation downstream** —
the regression is green against a generation nothing will collect.

**P2 (MANDATORY — run the real §11 operator command against the `_v3` pack).** Reproduce the
seat's own executed F4, but on the current family:
```
python3 scripts/record_window_duration_margins.py --pack-root configs/campaigns/d117_floor_qwen25_1p5b_v3 ...   # exact runbook §11 shape
```
*Falsifier:* a PASS (or a clean fail-closed refusal for a *data* reason such as
`member_missing` on empty runs) means the grant generalises across generations. A
`REFUSE authoritative_input_invalid — v2_authentication_forbidden_json_key` on the `_v3`
spec would mean **the blocker was cured only for the generation that was frozen at council
time**, and the seat is looking at L4-B1 reincarnated.

**P3 (does the r5→r6 supersession leave stale pins?).** Both generations are live by design
("eras retained forever", D-146). Enumerate every site and classify each as
intentional-dual-generation vs stale:
```
grep -rn "n17_r5\|n17_r6\|n19_r5\|n19_r6" --include="*.py" --include="*.json" joulewise scripts configs
```
Observed by this assembler: `calibration_bracketing.py` r5×3 / r6×3; `arm_readiness.py`
r5×1 / r6×1; `scripts/floor_mint_pinsets/schema_v2.json` r5×1 / r6×1; `_v3` packs and `_v3`
specs r6-only; both acceptance artefacts present.
*Falsifier:* any site that **selects** (rather than merely registers or dispatches on) r5 for
a `_v3`/freeze-0003 artefact is a stale pin and a claim-path defect. Cross-check against
`15-amendment-r6.md`'s executed assertion: "`configs/campaigns/d117_*_v3/generate_configs.py`
SUCCESSOR_ACCEPTANCE_ID = `d079_calibration_acceptance_v2_n17_r6`" — verify all three
generators, not one.

**P4 (the r6 reissue was forced by a fix round — re-verify the invariant it broke).**
`15-amendment-r6.md` records: "That verification was TRUE OF THE DESIGN and FALSIFIED BY A
FIX ROUND … Recorded as an instance of the general rule that fix rounds can invalidate
design-time verifications, which is why the delta re-audit re-verified the pin state (S1
contract lens: all four pins match head bytes at every commit boundary)."
*Falsifier:* re-run that pin check at the **current** tip `b92b43d` — one commit beyond the
`4597ad4` the packet names, and beyond `8b2b021` (S5 COMPLETE). If any of the four
D-079-pinned estimator sources has changed since the last delta re-audit boundary, the same
class of failure has recurred and an r7 is owed. This is the highest-value probe on the row:
the packet documents the failure mode and then advances the head past the verification.

**P5 (is the D-146 claim barrier itself sound? Nobody has audited it).** The barrier is
post-council, branch-only, and lands in five L4-scope modules. Read
`joulewise/uncertainty_evidence.py:1299-1330` and every consumer
(`analysis_engine/claims.py:136,174`; `whole_window.py:200`; `floor_extraction.py:191`;
`calibration_bracketing.py:1280,2123,2128`) and ask whether the predicate is reachable on
every claim path or only the ones enumerated in D-146's "ratified union site census".
*Falsifier:* a claim-producing path that consumes an anchor-v2-era bundle **without**
consulting `CLAIM_BEARING_ANCHOR_METHODS` would falsify D-148 cl.(7)'s assertion that the 748
stored anchor-v2 bundles are "**mechanically** enforced" as non-claim-bearing — turning a
registered limitation into an unenforced one.

**P6 (L4-2 is claimed unbuilt — verify, and check whether it is even still the right
target).**
```
grep -rn "d117c15v7" --include="*.py" joulewise scripts
sed -n '40,70p' joulewise/analysis_manifest_v3.py
ls -d configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_*
```
*Falsifier:* any production builder reaching the GAMMA grammar refutes NO-REPAIR-FOUND. If
confirmed unbuilt, the seat should additionally rule whether the work order still names the
right artefact — it was written against the `_v1` contrast pack and there are now three.

**P7 (L4-3 is claimed unrepaired — verify across the whole runbook, not just §11/12).**
```
grep -n "plan_tree" docs/phase_2/window_runbook.md
grep -rn "pack_tree_sha256" docs/phase_2/ scripts/record_window_duration_margins.py
sed -n '165,185p' docs/phase_2/three_night_freeze_manifest.md
```
*Falsifier:* a close-out step anywhere that compares `receipt.pack_tree_sha256` to the frozen
pack's committed `plan_tree.sha256` refutes NO-REPAIR-FOUND. Also check whether the recorder
CLI now *prints* the plan-tree sha (the work order's optional half) — that alone would make
the check a one-line operator diff.

**P8 (re-run the two structurally-succeeding F3 attacks at the current head).** The seat
executed F3-B (repinned truncated pack → plausible PASS) and F3-C (sha-repaired truncated
receipt → validator accepts) against `_v1`. Re-run both against a copy of a `_v3` pack.
*Falsifier:* if either now fails closed, something in the S0–S5 chain incidentally cured
L4-3 and the row should be re-dispositioned on that evidence rather than left open.

**P9 (the 24/27 denominator has never been attacked — attack it).** Apply the L2 re-audit's
procedure (`docs/process_traces/2026-08-15-l2-reaudit/reaudit-prompt.md`) to L4: enumerate
independently from the charter's L4 nouns without being shown the number 27, run negative
procedure-sensitivity probes, and run the adversarial coverage attack table.
*Falsifier:* if independent enumeration returns 27, the self-nominated universe holds. Given
that L4's universe named **three** pack families' worth of artefacts that have since become
**nine**, plus a new claim barrier in five modules and a new era system, a denominator of 27
returning unchanged would itself be suspicious. Note the L2 precedent: 15/16 self-reported
became **251** under attack.

**P10 (ED-QUAL-L4-1's evidence is outside the repo and was not read).** Read
`~/JouleWise-window-custody/ed-qual-20260817/decisive-replay.log` directly and extract: the
HEAD the run executed at; whether the run used the pre- or post-`1500265` script; and whether
the two named skipped tests (`test_coordinated_report_and_pin_change_refuses_against_floor_evidence`
and the split-partition test) appear as executed selections among the 23.
*Falsifier:* a HEAD at or provably equivalent to the audited head, with both named tests
executed, closes the row cleanly. Anything less means the row is closed against a different
artefact than it names.

**P11 (the registered limitation may not be registered where the paper will look).**
`grep -rn "check-to-grant" docs/` finds it in `decision_log.md`, `council_log.md`, two run
reports, and two trace dirs — but **not** in `docs/risk_register.md` (newest rows R-019,
R-020). D-139 A1 says "The paper states the assumption once, plainly."
*Falsifier:* locate the paper-side statement of the in-process-adversary assumption. If none
exists, an accepted-limitation ruling has no publication-side discharge, and D-148 cl.(6)'s
whole four-mechanism family inherits the same gap.

---

## 6. OPEN ITEMS FROM THIS ROW

- **The packet does not agree with itself about the current head.** Task brief `4597ad4`;
  `_ASSEMBLER-BRIEF.md:12` `d10881b`; actual `wtS0` tip `b92b43d`. Under amendment 12 the
  seat cannot adjudicate without a ruled head.
- **The branch gained two commits (`b92b43d`, `7305e0d`) while this packet was being
  assembled.** The head is live. An amendment-12 sitting requires a frozen, named head.
- **L4's amendment-12 exemption no longer holds.** The seat's own report claimed exemption
  because "no file in L4 scope changed after the manifest"; 214 commits later, most of L4's
  scope has changed — including `reduce.py`, `uncertainty_evidence.py`, `whole_window.py`,
  `analysis_engine/claims.py`, `floor_extraction.py`, and every frozen spec and pack.
- **Only ONE of the four L4 work orders was ever registered as a queue row.**
  `grep -n "WO-L4-" TASK_QUEUE.md` returns nothing; the only trace is
  WO-MARGIN-RECORDER-AUTHZ at line 105. **WO-L4-2, WO-L4-3, and WO-L4-4 have no queue
  existence at all** — they cannot be tracked to closure by the queue.
- **L4-2: no repair located.** Zero production references to `d117c15v7`;
  `analysis_manifest_v3.py` splitwise pin and `swdec-contrast` grammar unchanged. Searched:
  `joulewise/`, `scripts/`, `TASK_QUEUE.md`, the Completed Queue table.
- **L4-3: no repair located.** No `plan_tree.sha256` close-out comparison anywhere in
  `window_runbook.md`; the D-133 item (1) row still says "record its path and SHA-256 at
  close-out" only. Searched: the whole runbook, `three_night_freeze_manifest.md`,
  `TASK_QUEUE.md`.
- **L4-4: no repair located** (record-only). Searched: `TASK_QUEUE.md`, Completed Queue.
- **The D-133 item (1) freeze-manifest checklist row that WO-L4-1 ordered re-executed against
  frozen bytes is still an unchecked `- [ ]`** at `three_night_freeze_manifest.md:170`.
- **The L4-1 committed regression binds the `_v1`-generation spec and packs**
  (`tests/test_window_duration_margins.py` `_floor_spec_path`, and pack constants
  `d117_floor_qwen25_{1p5b,7b}_v1`) while the live family is `_v3`/r6 — the
  synthetic-fixture/real-vocabulary seam the cure was built to close may have reopened one
  generation downstream. **Not executed by this assembler; probe P1/P2 required.**
- **The D-146 claim barrier is post-council, branch-only, lands in five L4-scope modules,
  and no seat has audited it.** D-148 cl.(7) leans on it to make 748 stored bundles
  "mechanically" non-claim-bearing.
- **The r5→r6 supersession was forced by a fix round editing two of the four D-079-pinned
  estimator sources**, and the packet's named head (`4597ad4`) is already one commit behind
  the actual tip — i.e. the head has advanced past the delta re-audit boundary that
  re-verified the pin state.
- **ED-QUAL-L4-1's primary evidence (`decisive-replay.log`) lives outside the repo and was
  NOT read by this assembler.** The PASS is attested only by the T10 run-report table row.
  The run was at a later head, took three attempts, and two of its aborts were cured by
  patching the decisive test (`724ea28`) and the replay script (`1500265`) mid-session.
- **The two skipped decisive tests the row was meant to close were not shown running
  un-skipped at the current head.**
- **The check-to-grant registered limitation is absent from `docs/risk_register.md`** (newest
  rows R-019/R-020), and D-139 A1's requirement that "the paper states the assumption once,
  plainly" has no located paper-side artefact.
- **L4's 24/27 coverage denominator was never adversarially tested** and no re-enumeration at
  the current head exists — the standing obligation at `council-verdict.md:20-22` is
  unaddressed for this seat.
- **No runtime probes were executed by this assembler** (read-only mandate). Every "NO-REPAIR-
  FOUND" above is a static-analysis finding from grep/sed over the tree at the `wtS0` tip.
