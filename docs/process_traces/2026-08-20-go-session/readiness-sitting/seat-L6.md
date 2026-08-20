# SEAT L6 — PRODUCER→CONSUMER SEAM A (CONTRACT lens) — GATING
## READY-CANDIDATE COUNCIL SITTING, 2026-08-20

**Sitting head:** `5bd7acf` (Merge PR #160 — integration/phase2-transaction). Worktree
`…/scratchpad/wtRC-OPUS`, read-only, no tracked file modified.
**Baseline:** `8937dec`. **237 commits** separate them (the packet's "214" and ROW-L6's "215" are
both stale; recorded per the charter's honesty requirement).

---

## 0. ROW VERDICT

> ## **NOT-READY** (eight standing findings, seven of them unrepaired) — **plus an independently
> disqualifying UNVERIFIED on the coverage line.**

**Form note on the charter conflict in my brief.** My seat brief asked for
`READY / CONDITIONALLY-READY(conditions) / STILL-OPEN(remains)`. The binding charter form
(`docs/process/instrument-readiness-audit-charter.md:79-91`, reproduced verbatim at
`01-SESSION-BRIEF.md:28-40`) **deleted READY-WITH-CONDITIONS** and admits exactly
`READY / NOT-READY(+work orders) / UNVERIFIED`. The brief says "charter seat form"; the charter
wins. I record no conditional pass. The council should note the vocabulary drift in the seat briefs
themselves — it is the same fail-open shape the charter amendment was written to close.

**Single strongest reason (one sentence, as required):**
**B2 was never repaired — the cure was fresh data, not changed machinery; the project has itself
ruled that data dies today (`MAGISTRATE-RULING.md:23-42`: "the fuse LAPSES … the `_v4` re-freeze is
compelled"), so within hours of this sitting there is again no armable pack family, and the
operative night document — `docs/phase_2/window_runbook.md` — contains ZERO occurrences of the live
`_v3` family or `freeze-0003`, naming instead the superseded `_v2` family ten times and the retired
measurement checkout `/Users/edr/JouleWise-measurement-20260813` nine times.**

---

## 1. ENUMERATED EVIDENCE UNIVERSE (independently enumerated at `5bd7acf`, not inherited)

The 2026-08-15 not-certified-complete ruling (`council-verdict.md:18-22`) forbids me from inheriting
the seat's self-nominated 40-node denominator. I enumerated mechanically, from closed sets:

| Universe | How enumerated (mechanical, reproducible) | Size |
|---|---|---|
| **U1** — arm-plane obligation rows | parsed `configs/arm_readiness/d117_row_registry_v1.json` → `rows[]` | **35** |
| **U2** — distinct required evidence kinds over U1 | `Counter(r['required_evidence_kinds'])` | **29** |
| **U3** — schema IDs declared in code | regex `"joulewise\.[a-z0-9_.]+\.v\d+"` over every `.py` in `git ls-files joulewise scripts` → scratch `opus-L6-scratch/schema-census.txt` | **140** |
| **U4** — this row's findings + ED rows | packet | **8 + 2** |

**COVERAGE, stated so it survives an adversarial re-count:**

- **U1: 35 / 35** — every registry row traced to a producer route at this head.
- **U2: 29 / 29** — every evidence kind traced to a producer module or an internal arm-time pass.
- **U4: 10 / 10** — every finding and both ED rows independently re-verified with executed probes.
- **U3: NOT re-enumerated to producer+consumer depth.** I traced the arm / T-0 / freeze subset
  (~40 of 140). The post-collection, mint, launch-lineage and claims planes I did **not** re-trace.

> **Therefore the coverage line is UNVERIFIED, and I record it as such.** The seat's original
> denominator was 40 "artifact-class nodes"; the code-side ID universe is now **140** against the
> seat's own "~120" cross-check (`L6-SEAM-READER-A-report.md:10`). The council ordered independent
> re-enumeration of every universe as a standing packet element; for L6 that re-enumeration has
> been performed for the **arm plane only**. Charter amendment 11 makes UNVERIFIED independently
> disqualifying — this alone bars a council READY even if every finding above had closed.

**Falsification of my own denominator (attempted, as required).** I tried to break U1/U2 by asking
whether the registry is the wrong closed set — i.e. whether the `_v3` freeze receipts bind a
*different* registry. `freeze-0003.json.row_registry` names
`configs/arm_readiness/d117_row_registry_v1.json`, sha `d248fdc5…`, which is the file I parsed. U1/U2
survive. U3 I could not defend and did not claim.

---

## 2. PER-FINDING DISPOSITIONS

### F1 / B1 — T-0 evidence author's inputs have no producer → **NOT-READY (producer half discharged; the row does not close)**

**Repair verified present at `5bd7acf`, all on `origin/main`:**
- `scripts/capture_t0_step.py:59-66` `STEP_FILENAMES` = exactly the six captures the finding named;
  `:41` `INPUT_DIRECTORY = "arm_readiness.t0.inputs"`; `:38-40` declares the three T-0 schemas incl.
  `joulewise.arm_readiness_t0_command_capture.v1` — the schema the finding said only the author
  referenced. Derived inputs at `:516-533` (`arm-context.json`, launch manifest) and the clock
  attestation at `:597`. **All nine named inputs have a shipped producer.**
- Runbook steps exist and the line citations hold at this head:
  `docs/phase_2/window_runbook.md:913,922,931,942,952,963` (E-4…E-9a), `:994` (E-9b author),
  `:1020` names `arm_readiness.t0.inputs`. The finding's "the runbook never names
  arm_readiness.t0.inputs" is **false at this head**.
- Merge status **cured by the wave** (this is the P-13 cure, verified by me, not assumed):
  `git merge-base --is-ancestor <sha> origin/main` returns true for **all thirteen** commits the two
  assemblies list as branch-only — `1d3873b`, `3a75a77`, `5e38f1e`, `eb7f6c6`, `94dc3b3`, `8b2b021`,
  `a61ac92`, `65cc0f3`, `d8d2022`, `32cf987`, `0f886d3`, `47d2645`, `00ec3b7`.
- **15 receipts still 15.** The ED-row probe asked whether D-146/D-147 moved the count. Executed:
  ARM_ONLY ∧ ALWAYS rows minus `{GIT_CHECKOUT, DRY_RUN_REHEARSAL}` = **15**, matching
  `tests/test_arm_readiness_evidence_t0.py:923-926` ("must account for exactly the fifteen receipts").

**Why the row does not close — three residuals, two of them executed:**

1. **EXECUTED FALSIFIER — the authoring path REFUSES at the sitting head.** Calling
   `capture_t0_step._verify_terminal_review(Path('.'), pack, pack_sha256=…)` at `5bd7acf` raises
   `CaptureT0Error: reviewed checkout is dirty or differs from local/origin main`. Root cause,
   measured: `arm_readiness.reviewed_main()` returns
   `head_commit 5bd7acf…, local_main_commit b9e197a…, origin_main_commit b9e197a…, clean true,
   exact_match FALSE` — **`main` advanced from `5bd7acf` to `b9e197a` DURING this sitting.** The
   diff is `README.md` + `RUN_STATE.md` only (`git diff --name-only 5bd7acf..b9e197a` hits nothing
   under `joulewise|scripts|configs|tests`, so every code citation in this report holds), but the
   contract consequence is exact: **a docs-only bookkeeping commit to `main` disarms the entire T-0
   producer.** This is P-13's pathology recurring inside the sitting convened to cure it, and it is
   an availability property of the seam that no document names.
2. **EXECUTED FALSIFIER — the tool has never been run.**
   `find /Users/edr/JouleWise-window-custody /Users/edr/JouleWise-measurement-20260818 -name
   "arm_readiness.t0.inputs" -type d` returns **nothing**. The PASS side of the arm-plane producer
   seam remains unproven (= ED-QUAL-L6-1, §4). I did run the producer in the sandbox against scratch
   custody and it failed closed at two distinct guards —
   `evidence_author_t0_capture_environment_invalid` ("window-plan root must be inside the D-134
   custody root") and `evidence_author_t0_capture_io_error` — writing zero bytes. **Refusal side
   confirmed; PASS side still unobserved, exactly as at the baseline.**
3. **The terminal-review remedy is half-built, and the contract was honestly weakened.** The
   *verifier* is real and fail-closed (`scripts/capture_t0_step.py:288-317`, duplicated at
   `joulewise/arm_readiness_evidence_t0.py:931-937`, requiring exactly one each of
   `JouleWise-Terminal-Review: PASS` / `-Tree-Oid` / `-Pack-Sha256`). The **producer is a human
   `git commit --allow-empty` ceremony** — `git grep -l "allow-empty" -- scripts/` returns nothing.
   The Addendum's other half ("whose commit the superseding manifest pins") is unbuilt: the manifest
   has one commit ever (`694442c`) and still names `ac3fe1d`. And the ordered step at
   `window_runbook.md:815` still says `cd /Users/edr/JouleWise-measurement-20260813` — run verbatim,
   the ordered attestation attests the **wrong tree**.

**On the honest weakening (adjudicated, not deferred).** `capture_t0_step.py:1-11` and
`window_runbook.md:880-890` now state plainly that v1 "does not defend against deliberate operator
fabrication," and D-148 clause 6 (`docs/decision_log.md:171`) **accepts** T-0 capture provenance as a
registered limitation. I rule that this **legitimately disposes of the finding's authenticity
premise** ("boot-bound monotonic-ns fields no human can hand-produce") — a scenario premise retracted
by ruling is retired, not silently failed. What it does **not** dispose of is the finding's operative
half: the producer must actually run, once, end to end. It has not.

**Sibling-only rider disposed:** `15-ROW-L6-seam-reader-A.md:85-88` flags the unanswered Ed/advisor
paper-scope RULING-REQUIRED at `docs/decision_log.md:9638-9647` (trusted-operator evidence vs. an
App-Attest signed-capture route). Verified still unanswered — the only occurrence of
"signed capture"/"App Attest" in the log is the question itself. **Disposed as out of this charter's
scope:** it is recorded PAPER-SCOPE and non-blocking by its own terms, and D-148 cl.6 disposed the
engineering half. It does not bear on this row's verdict.

---

### F2 / B2 — freeze horizon + refresh lane → **NOT-READY (the strongest finding in the row)**

**What genuinely got built (credited in full):** the successor-pack lane exists and ran twice.
Freeze receipts are now `joulewise.arm_readiness_freeze_receipt.v2` with a first-class `predecessor`
block (`freeze-0003.json` → predecessor `freeze-0002`, sha `1277103b…`), so the contract refuter's
"freeze-0001 hardcoded" defect is gone. **Executed positive probe:** all three `_v3` packs'
`pack_identity.plan_sha256` reproduce **byte-exact** at `5bd7acf`
(`9ab4776f…`, `0ae5576b…`, `56ed0e53…` — recomputed, MATCH True ×3). The freeze receipts authenticate
at this head. That is real and it is more than the finding had.

**Why the finding stands anyway — four legs, three of them executed:**

1. **The 24 h + same-boot mechanism is untouched, and the data cure expires today.**
   Live probe at 12:26:09Z: `now_monotonic_ns 2452817805075250`; min `valid_until` per family
   2468742407178458 / 2468774933440083 / 2468792444508708 → **headroom 15,924 / 15,957 / 15,974 s
   ≈ 4.42 h**, lapsing **≈2026-08-20T16:51Z**. Boot session `DA90818C-…` unchanged (verified
   `sysctl -n kern.bootsessionuuid`). The ruled disposition is **LAPSE**
   (`docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING.md:33-42`: "the fuse LAPSES. No
   pre-17:00Z window attempt … The `_v4` re-freeze is compelled by the fuse regardless"). **So the
   sitting's own verdict outlives the armability of every pack it could bless.** The finding's
   words — "a required output (a valid GO arm receipt) currently has no producible path" — become
   literally true again, by ruling, hours after this sitting.
2. **The operative night document names neither the live family nor the live checkout.**
   `grep -c "_v3" docs/phase_2/window_runbook.md` = **0**; `freeze-0003` = **0**; `20260818` = **0**.
   Against that: `_v2` = **10** hits, `/Users/edr/JouleWise-measurement-20260813` = **9** hits,
   including the frozen `window.env` literals at `:189,192,193,201,202,204` and the terminal-review
   step at `:815`. `grep -n "re-freeze\|refresh lane\|freeze-refresh\|re-author"` over the runbook
   returns **exactly one hit** — `:1012`, the T-0 namespace paragraph. The lane lives only in
   `docs/process/phase2-transaction-runsheet.md`, whose own title scopes it as a **one-time Phase-2
   transaction**, not a repeatable window-day lane. **The "no operative document names the lane"
   half of B2 is untouched — and it has gotten worse, because the runbook was updated to `_v2` and
   the family then rotated to `_v3` without a runbook pass** (RUN_STATE's own recovered-work ledger
   lists "runbook `_v2`→`_v3` pass" as unexecuted). With `_v4` compelled, the night document is
   about to be **two families stale**.
3. **The R1 lifecycle is dormant — and is now RULED to stay dormant.** Executed: the only committed
   registry is `d117_row_registry_v1.json`, `schema_version = joulewise.arm_readiness_row_registry.v1`,
   with **no** `freeze_evidence_lifecycle` key (parsed); `git grep -l
   "arm_readiness_row_registry.v2" -- configs` returns nothing. At `arm_readiness.py:5372-5375` and
   `:5210-5212` `lifecycle_registry` is derived **only** when the schema is v2 — so on production
   packs it is `None`, and therefore `expected_head_commit` is `None` too. D-148.5 ruled the install
   **deferred to the `_v4` boundary** (`MAGISTRATE-RULING.md:23-31`), on three grounds including a
   byte-pin **CONFIRMED-BLOCKER**. **I reproduced that blocker's mechanism independently:** supplying
   a non-matching `expected_head_commit` to `_authenticate_generic_evidence_item` refuses
   `evidence item is stale for pack or HEAD` — and every one of the 33 `_v3` receipts carries
   `head_commit 1d3873bb…` while `reviewed_main()` at this head yields `5bd7acf…`. Activating R1 on
   `_v3` would refuse all 33. The deferral is correct; the consequence for my row is that the
   head-binding and `V1_GRANDFATHERING` defenses **do not fire on any pack this council could bless**.
4. **Charter amendment-12 exposure unresolved.** `docs/process/audit-baseline-manifest.json` has
   exactly one commit (`694442c`), still pins `head_commit`/`origin_main` = `ac3fe1d…` and the three
   **`_v1`** digests, and carries **none** of the three ruled supersession fields
   (`pack_digest_algorithm`, chain-template coverage note, binding paths). The re-freezes that cured
   the lapse are precisely the pack-byte changes that void it.

---

### F3 / S2 — stage-1 `floor_mint_pin_requirements.v2` → **NOT-READY, NO-REPAIR-FOUND**

Executed: `git ls-files | grep -i pin_requirement` → empty. The ID exists in exactly two places —
`scripts/mint_floor_artifact_generalized.py:64` (constant) and
`scripts/floor_mint_pinsets/schema_v2.json:976`. The only consumer is a **presence**-rejecting guard
at `scripts/mint_floor_artifact_generalized.py:1416-1417`
(`raise MintError("desk-stage pin requirements are non-mintable")`). **Absence is still silent** —
exactly as filed. No subsumption ruling located. A post-hoc pinset remains mechanically
indistinguishable from one honoring the two-stage freeze; the pre-registration value D-117 ordered is
absent.

### F4 / S3 — hashed postcollection backup receipts → **NOT-READY, NO-REPAIR-FOUND**

Executed: `grep -c "sha256\|shasum" scripts/backup_runs.sh` = **0**;
`git log --oneline 8937dec..HEAD -- scripts/backup_runs.sh` = **0 commits** across all 237. §12 still
demands two receipt-path+SHA-256 records (`window_runbook.md:1807-1810`) that no tool emits.
**ID-COLLISION CONFIRMED AND UPHELD** — `council-verdict.md:44-45` Disposition 4 strikes
"F4's timing premise," which is cluster-B refuter F4 = **L8-B3** (the `sudo -n systemsetup` /D-004
privilege finding), **not** this item. rows/ROW-L6.md's warning is correct; the sibling assembly does
not carry it. **Nothing in L6's row was struck.**

### F5 / S4 — FINAL arm packet stale → **NOT-READY, NO-REPAIR-FOUND (aggravated)**

`audit-baseline-manifest.json:3` still cites
`arm-packet-alpha-FINAL-20260813.md`. No successor packet exists in repo, custody, draft or queue.
Its gate condition (Phase-2: T-0 repair passing end-to-end at the exact reviewed head) is **unmet by
my own executed probes** (§F1 items 1-2), so the row **cannot** close by design — I record that as a
**dependency, not a defect**, per the sibling's correct framing. What *is* a defect: staleness grew
by a family rotation (`_v1`→`_v3`, with `_v4` compelled), ~+422/−124 runbook lines, and D-149's
wholesale T-0 GO-regime rewrite. The nearest new document,
`docs/process/rehearsal-operator-card.md:3`, self-declares "qualification choreography evidence,
never claim evidence" and targets `_v2`.

### F6 / N1 — margins receipt has no machine consumer → **NOT-READY, NO-REPAIR-FOUND**

Executed: `git grep -ln "window_duration_margins_receipt" -- joulewise scripts` returns exactly one
file, `joulewise/window_duration_margins.py` (the writer). PR #151 (`00ec3b7`) hardened the
recorder's **read authorization** (that is L4-B1); it gave the emitted receipt no reader. §11
ordering remains prose.

### F7 / N2 — `PRIVILEGE_INSTALLATION` has no producer → **NOT-READY, NO-REPAIR-FOUND**

Producer census over all 29 kinds (executed, §1): **exactly two kinds have no producer module** —
`PRIVILEGE_INSTALLATION` and `GIT_CHECKOUT`. I ruled `GIT_CHECKOUT` **not a gap**: its row
`desk.reviewed_checkout` is satisfied by an arm-time internal pass
(`arm_readiness.py:6181,6401` `internal_passes.add("desk.reviewed_checkout")`), which is a legitimate
producer route. `PRIVILEGE_INSTALLATION` remains genuinely producerless across four
`CLOCK_HELPER_ONLY`/`ARM_ONLY` rows. Safety condition holds and is hardcoded:
`scripts/capture_t0_step.py:438` emits `"clock_route": "MANUAL"`. **Correction on the record:** D-127
landed `scripts/joulewise-network-time.sudoers`, a network-time **toggle** fragment — *not* the
CLOCK_HELPER route. The nit's own caveat therefore survives intact, and the sibling's worry that
shipping the sudoers file makes the nit load-bearing is **refuted**: installing it does not move
`clock_route` off `MANUAL`.

### F8 / N3 — arm-time replay skips the horizon check → **NOT-READY, NO-REPAIR-FOUND; SEVERITY RE-GRADED nit → should_fix**

**This is the finding I attacked hardest, and it produced the sharpest executed evidence in this
report.** Three probes against the real `_v3` pack, using the *exact* call shape of the freeze replay:

| # | Probe | Result |
|---|---|---|
| **A** (positive) | `_authenticate_generic_evidence_item(item, pack, pack, expected_boot_session_id=boot, expected_head_commit=None, lifecycle_registry=None)` — i.e. verbatim the freeze-replay call | **AUTHENTICATED** (`ACCEPTANCE_OWNER`) |
| **B** (negative) | identical, plus `now_monotonic_ns = valid_until + 1` | **REFUSED — `readiness_record_expired`, "evidence item expired"** |
| **C** (negative) | identical, plus a wrong `expected_head_commit` | **REFUSED — "evidence item is stale for pack or HEAD"** |

Plus a source-level probe: `"now_monotonic_ns" in inspect.getsource(_freeze_evidence_for_arm)` →
**False**; same for `_load_freeze_reference`. **The horizon check exists, refuses correctly when
supplied, and is never supplied from the freeze path.** The defect is a missing argument at two call
sites (`arm_readiness.py:5253-5262`, `:5385-5392`), not a missing mechanism.

**Why I vacate my own seat's "nit."** The 2026-08-15 grading rested on "defense is one hop
downstream" plus a benign fact pattern. Both premises moved:
- The fact pattern becomes hostile **today at ~16:51Z**, by ruling, not by accident. From that
  moment, arm-time replay authenticates expired evidence and `FREEZE_AND_ARM` rows report **PASS**
  from it.
- D-149 (`docs/decision_log.md:172`) introduced **full no-hands automation** whose condition (2) is
  "the frozen pack's arm ceremony passes every gate **with freshness horizons honored**," checked
  off a template (`docs/process/d149-go-receipt-template.md:21`). Row verdicts are exactly the
  surface an unattended evaluator reads. A row that reports PASS from expired evidence is a
  fail-open surface for a regime that did not exist when the nit was graded.

The downstream defenses are still real and I verified them — the `min`-fold at
`arm_readiness.py:6230-6241` and the `readiness_record_expired` refusals at `:6497,:6501` — so
**consumption soundness is intact; nothing unsound is consumed.** The re-grade is about the *arm
receipt's row surface*, not about consumption. I converge with L7's severity on **new evidence**, not
by deference; the seam-B seat ran independently and I did not read its verdict.

---

## 3. SIBLING-DIVERGENCE ADJUDICATION (`rows/ROW-L6.md` vs `15-ROW-L6-seam-reader-A.md`)

Divergences are evidence. Eleven found; six are substantive.

| # | Divergence | Adjudication |
|---|---|---|
| 1 | **Mint guard line number.** rows/ cites `mint_floor_artifact_generalized.py:1391-1392`; 15- cites `:1416-1417` + constant `:64`. | **15- CORRECT.** Verified: the guard is at `:1416-1417`. rows/ carried the 2026-08-15 baseline line number forward without re-verifying at head. Substance identical; **citation stale**. This is exactly the class of drift the packet's own tree-moved addendum warned about. |
| 2 | **Which R1 governs the freeze horizon.** rows/ F2 table routes to D-147 / `2026-08-19-r1-r2-codesign/14-r2-ruling.md`; 15- warns those are a **different R1** (capture-pipeline v3) that says nothing about the PACK horizon. | **15- CORRECT and materially so.** Verified: `13-r1-ruling.md` has **zero** hits for `horizon|valid_until|monotonic`. The freeze-lifecycle R1 lives at `docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/` (present at head, four files). A seat trusting rows/'s table as the horizon authority is misrouted. |
| 3 | **Freeze-replay call sites.** rows/ names one (`_freeze_evidence_for_arm`); 15- names **two** (`_load_freeze_reference:5151` call `:5253-5262` as well) and locates the real enforcement `validate_r1_class_lifecycle:3344` with two call sites (`:4585`, `:6543`), neither on the freeze path. | **15- MORE COMPLETE; both verified by me.** A remedy written against rows/'s single site would leave the second uncovered. Folded into WO-L6-B. |
| 4 | **ID-collision on "F4".** rows/ carries an explicit warning that Disposition 4's struck F4 is L8-B3, not L6-S3; 15- is silent. | **rows/ CORRECT and the better catch.** Upheld above; without it a seat plausibly reads L6-S3 as struck. |
| 5 | **S2 search method.** rows/ probes `git ls-files \| grep -i pin_requirement` (filename-scoped); 15- greps file *contents* and finds the ID in two places. | **15- is the stronger evidence**; rows/'s probe cannot see a schema ID living inside a file. Same conclusion, better method. Both land on NO-REPAIR. |
| 6 | **Head/commit-count metadata.** rows/: HEAD `b92b43d`→`2243137`, "215 commits". 15-: HEAD `79a4cd0`. | **Both moot and both wrong at the sitting head.** Actual: `5bd7acf`, **237** commits from `8937dec`, and `main` advanced to `b9e197a` mid-sitting. Recorded, not held against either assembler. |
| 7-11 | Merge-status framing (rows/ "BRANCH-ONLY" ×13 vs 15- "main"), the "~5 minutes" S5 timing datum (15- only), the `head_commit 1d3873b` staleness (rows/ only), the `window_runbook.md:813` stale checkout (rows/ only), D-148 cl.6 acceptance (rows/ only). | **Complementary, not contradictory.** All verified. The BRANCH-ONLY framing is **wholly superseded** by the merge wave — all thirteen commits are on `origin/main` at `5bd7acf`. **The two assemblies are jointly complete and individually incomplete: neither alone would have supported this verdict.** That is a finding about the dual-assembly accident, and it argues for keeping it deliberately. |

**Net:** no divergence changes any disposition. Two (rows/ #1, #2) are defects in the row I was
assigned, and a seat reading only `rows/ROW-L6.md` would have cited a wrong line and a wrong ruling.

---

## 4. ED-QUALIFICATION ROW STATUS

### ED-QUAL-L6-1 (live T-0 authoring path) — **OPEN. Not closable as written.**

Executed falsifiers: (i) no `arm_readiness.t0.inputs` directory exists anywhere on the machine;
(ii) `_verify_terminal_review` refuses at the sitting head; (iii) the only committed choreography,
`docs/process/rehearsal-operator-card.md`, targets `_v2` — one family stale now, **two** once `_v4`
lands. Latest records still say OPEN (`docs/run_reports/2026-08-18-t10-session.md:110`;
`docs/process/ed-morning-packet-2026-08-18.md:126`); no later execution record exists.

**NEW FINDING FROM THIS SEAT — the row is now in direct contradiction with a ruling.** The row
demands "a same-boot `generate_arm_readiness.py arm` reaches row evaluation." D-148.5 B-4
(`MAGISTRATE-RULING-r3.md:74-81`) **redefines the clean-arm dry run to exclude any real arm**: "No
real arm is issued for ceremony — the first real arm of the `_v4` family is the shakedown window's
own, under its D-149 GO receipt." **So ED-QUAL-L6-1 as written cannot be closed until the first
funded window** — while charter amendment 10 (`charter:70-77`) says stable-capability rows are
"performed BEFORE the sitting … stable evidence cannot be deferred" and "only T0 rows may remain open
at the sitting." **The council must resolve this directly: either re-scope the row to the ruled
ceremony (dry-run + P1/P2/P3 probes), or reclassify it T0.** Leaving it as written makes the
clearance rule unsatisfiable by construction — which is a fail-open shape, because the pressure will
be to quietly call it closed.

### ED-QUAL-L6-2 (timed freeze-refresh rehearsal) — **OPEN (substantially exercised; deliverable absent), and now on a deadline that expires today.**

The lane ran twice for real (`_v2`/freeze-0002; `_v3`/freeze-0003 — `3a75a77`, `5e38f1e`, `eb7f6c6`,
`94dc3b3`, `8b2b021`, all now on `origin/main`). **Neither run produced the row's deliverable:** no
dry-run leg after `dry-run-0001` (2026-08-13), and no observed wall-clock for the *lane* — only
"~5 minutes" for the six mint commands (`ed-s5-mint-decision-2026-08-19.md:41`) and ~2m44s of commit
spacing. No "WO2 runbook amendment" naming a timed lane exists.

**Why this is now load-bearing rather than bookkeeping.** D-148.5 B-5
(`MAGISTRATE-RULING-r3.md:88-95`) orders that the compelled `_v4` transaction's **envelope
arithmetic** price the lane against the fuse, including Ed's unbounded step-6 turnaround and the
canonical-suite green time. **That arithmetic needs exactly the observed lane duration ED-QUAL-L6-2
was created to produce** — and `MAGISTRATE-RULING-r3.md:70-71` names the pre-fuse `_v3` rehearsal
harvest as "the only pre-commitment measurement opportunity," which **expires with the fuse at
~17:00Z today**. If it is not harvested before the fuse, the `_v4` envelope gets estimated, which is
the precise substitution the row was written to prevent.

**ED-row roll-up for this seat: 0 of 2 closed. Under charter:81-83, a council READY is unavailable.**

---

## 5. UNEXECUTED OBLIGATIONS (listed, per charter:59-68)

1. **U3 producer→consumer re-enumeration beyond the arm plane** — 140 schema IDs enumerated, ~40
   traced. Post-collection, mint, launch-lineage and claims planes not re-traced. *(This is the
   basis of my UNVERIFIED coverage line.)*
2. **End-to-end CLI `freeze`/`dry-run`/`arm`/`consume`** — not executed. `freeze` mutates pack bytes;
   `arm` requires B1 inputs that do not exist; the tree had to stay byte-identical. Carried over
   unresolved from 2026-08-15.
3. **The `t0.ledger_reservation` identity question handed to L2** — whether the predicate's
   `expected_plan_sha256` (pack `plan_tree` sha) and the reservation's `FROZEN_PLAN` sha are the same
   identity. D-147 may answer it; **I did not verify that it does** and the council must not assume so.
4. **Live collection-plane producers** (`run_campaign`, `validate_powermetrics_fiducial`,
   `reserve_calibration_window_bracket`) — no live measurement permitted; contract-read only.
5. **`FROZEN_PLAN`/`window.env` instance** — off-repo by design; none exists for the next window.
6. **The off-repo FINAL arm packet's contents** — I did not open
   `arm-packet-alpha-FINAL-20260813.md`; my F5 disposition rests on the manifest citation and the
   absence of a successor, not on re-reading the packet.

---

## 6. WORK ORDERS (required by the NOT-READY verdict)

| WO | Sev | Contract |
|---|---|---|
| **WO-L6-A** | blocker | Fold the freeze-refresh lane into the **operative night document** as a repeatable per-window lane: retarget `window_runbook.md` off `_v2`/`-20260813` (currently 10 + 9 hits, incl. the `window.env` literals `:189-204` and the terminal-review step `:815`) onto the live family and checkout, and make the retarget a **named step of every family transaction** so a rotation cannot again outrun the runbook. Acceptance: zero `_v2`/`20260813` hits in operative steps; a §-numbered refresh lane carrying WO-L6-B2's observed duration. |
| **WO-L6-B** | blocker (re-graded from nit) | Pass `now_monotonic_ns` at **both** freeze-replay call sites (`arm_readiness.py:5253-5262`, `:5385-5392`) — or register a limitation stating that `FREEZE_AND_ARM` rows may report PASS from expired evidence and bar D-149 auto-GO from reading row verdicts. Defect-shaped regression asserting refusal at `valid_until + 1` (probe B above is the test). |
| **WO-L6-C** | blocker (form) | **Resolve the ED-QUAL-L6-1 contradiction** (§4): re-scope to D-148.5 B-4's ceremony, or reclassify T0. Lieutenant-forbidden — this is charter interpretation. |
| **WO-L6-D** | should-fix | Harvest ED-QUAL-L6-2's **observed lane wall-clock before the fuse**, and fold it into the `_v4` envelope arithmetic that D-148.5 B-5 orders. Deadline ~17:00Z today. |
| **WO-L6-E** | should-fix | Rule or build stage-1 `floor_mint_pin_requirements.v2`: commit an instance + an absence check, **or** record a ruling that D-147's resolver supersedes the two-stage design and delete the constant (`:64`) and `schema_v2.json:976` as dead vocabulary. |
| **WO-L6-F** | should-fix | Hashed postcollection backup receipts for both roots in `scripts/backup_runs.sh`, or amend §12 (`window_runbook.md:1807-1810`) to what the tool can produce. |
| **WO-L6-G** | should-fix | Successor arm packet at the `_v4` family, sequenced after the end-to-end T-0 pass at the exact reviewed head; retire the 2026-08-13 packet's citation in the superseding manifest. |
| **WO-L6-H** | nit | Give `window_duration_margins_receipt.v1` a machine consumer or delete §11's ordering obligation. |
| **WO-L6-I** | nit | `PRIVILEGE_INSTALLATION`: build the producer or delete the four `privilege.*` rows and predicate specs as dead code — **decided before any `clock_route ≠ MANUAL`**, not after. |

---

## 7. CONCRETE FAILURE SCENARIO PER KEPT FINDING (charter:59-68)

- **B1.** The lead runs the terminal-review ceremony, then a routine RUN_STATE commit lands on
  `main` — as one did *during this sitting*. `reviewed_main().exact_match` flips false, every
  `capture_t0_step` invocation refuses `evidence_author_t0_capture_terminal_review_missing`, and
  the operator, with a quiet machine and a funded night, has no document telling them the cause is a
  docs commit by another agent. Night ends NO-GO.
- **B2.** Post-17:00Z today, the operator follows `window_runbook.md` verbatim: it points at
  `_v2` packs in `/Users/edr/JouleWise-measurement-20260813`, a family and a checkout that are both
  retired. If they instead reach for `_v3`, all 33 receipts are lapsed and the arm receipt is expired
  at birth; the runbook names no refresh lane. The only lawful path is the `_v4` transaction, which
  the night document does not describe.
- **S2.** The window runs; the pinset is assembled post hoc; nothing refuses; the paper claims a
  pre-registered two-stage freeze that no artifact can evidence.
- **S3.** §12 close-out asks for two hashed backup receipts. The operator hand-writes them or skips
  them. A silently failed backup surfaces only if a human audits the record.
- **S4.** The operator opens the newest packet in custody (2026-08-13), which has no T-0 authoring
  step and says "expect a refusal unless §0.6 has been resolved," and walks into a wall of readiness
  refusals with no packet row explaining them.
- **N1.** A tired operator skips §11; the comparative-cell margin record is lost with no mechanical
  signal.
- **N2.** A future arm context selects the clock-helper route; four rows become applicable with no
  production path; guaranteed NO-GO with no tooling recourse.
- **N3.** After 16:51Z, an unattended D-149 evaluator reads `FREEZE_AND_ARM` rows showing PASS from
  expired evidence and records condition (2) — "freshness horizons honored" — as satisfied. The
  window still fails closed at consume, so the cost is a wasted quiet night and a GO receipt whose
  condition (2) line is false on its face.

---

## 8. WHAT WOULD MAKE THIS ROW READY

Not a condition list — the charter has no conditional pass. This is the shortest true path:
WO-L6-A + WO-L6-B land; WO-L6-C resolves the ED-row contradiction; ED-QUAL-L6-1 is then *performed*
against the `_v4` family and its receipts custodied; ED-QUAL-L6-2's duration is harvested and folded
into the `_v4` envelope; the Phase-3 supersession issues with its three ruled fields; and the U3
producer→consumer re-enumeration is executed so the coverage line can leave UNVERIFIED. Until then
this seat is NOT-READY, and its coverage is UNVERIFIED.

---

*Seat L6, contract lens, GATING. All probes executed read-only at `5bd7acf` in
`…/scratchpad/wtRC-OPUS`; scratch and the schema census in
`…/scratchpad/ready-sitting/opus-L6-scratch/`. No tracked file modified.*
