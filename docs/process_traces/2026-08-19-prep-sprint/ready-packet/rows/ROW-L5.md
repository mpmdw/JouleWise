# ROW L5 — PACK / READINESS / CUSTODY (gating seat, xhigh tier)

> **Assembler note on the tree actually read.** The assembler brief names HEAD `4597ad4`. The
> read-only worktree
> `/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtS0`
> is on branch `impl/r2-s0-mint-resolver` at **`b92b43d`**, one commit ahead of `4597ad4`
> (verified ancestor). All "current head" statements below are at **`b92b43d`**. Nothing is merged
> to main (`RUN_STATE.md:138` — "NO MERGE HAS OCCURRED").

## 0. Seat identity and 2026-08-15 result

- **Seat:** `L5-PACK-READINESS-CUSTODY`, gating, xhigh.
- **Seat verdict as recorded:** **NOT_READY** (`raw/L5-triage.md:6`; seat report §7 line 84:
  "**NOT-READY**, with three bounded work orders…").
- **Coverage:** **16 / 18** (`evidence_universe_count = 18`; `raw/L5-triage.md:7`; seat report
  line 28: "**Coverage: 16/18** universe classes examined; the two unexamined classes are listed
  plainly above and in §5" — U17 CI behavior and U18 live arm-night executions).
- **Findings:** 5; **falsifiers:** 8 (`raw/L5-triage.md:8`; seat report §3 table N1/N2/F1–F6).
- **Sitting verdict:** `docs/process_traces/2026-08-15-readiness-council/council-verdict.md`
  **lines 10–16** ("**NOT-READY. 0 READY / 11 NOT-READY** … **No funded window may be armed.**"),
  with the standing caution at **lines 18–22** ("**The work-order program is NOT CERTIFIED
  COMPLETE**").
- **Seat report path:**
  `docs/process_traces/2026-08-15-readiness-council/seat-reports/L5-PACK-READINESS-CUSTODY-report.md`
  (83 lines).
- **Cold adjudicator's summary of this seat** (`cold-fable-ruling.md:23`): "| L5 Pack/readiness/custody
  (gating) | NOT-READY | 3 should-fix (incl. self-polluting plan tests, stale dry-run binding),
  open ED row. |"

---

## 1. FINDINGS — original text verbatim, with citation

### F1 — [should_fix]
**Title (verbatim):** Floor-pack plan tests self-pollute the frozen packs and fail
deterministically from a clean tree; CI-green status unexplained

**`file_line` (verbatim):** `tests/test_d117_floor_qwen25_1p5b_plan.py:30-35,259-264 (same pattern
tests/test_d117_floor_qwen25_7b_plan.py:256)`

**failure_scenario (verbatim):**
> python3 -m unittest tests.test_d117_floor_qwen25_1p5b_plan from a byte-clean tree: the
> module-import exec of the pack generator writes __pycache__/generate_configs.*.pyc INTO the
> frozen pack directory and the inventory test (rglob without a __pycache__ filter) fails —
> reproduced on python3.13 and CI's python3.11. Consequences: (a) the pack-integrity literal-pin
> layer (the main automated catch for committed plan_tree drift, per falsifier F6) is red or
> red-masked in CI — how #149 passed CI is unexplained and needs the CI log pulled; (b) any
> pre-arm plan-test run in the measurement checkout leaves __pycache__ inside the frozen pack,
> after which every committed_pack_tree_sha256 caller (t0 author, arm, consume) REFUSES 'untracked
> pack directory' until it is manually removed — a 3am tripwire (refusal executed live). The
> contrast test already carries the known fix (tests/test_d117_decode_contrast_plan.py:59-65,
> commit e286e75).

**Seat-report citation:** L5 report **line 59** (F-1) and **line 47** (falsifier N2: "Foreign file
(`__pycache__`) inside a frozen pack → **REFUSED** `readiness_pack_not_committed` (untracked pack
directory), .gitignore notwithstanding").

### F2 — [should_fix]
**Title (verbatim):** Generator --check echo hole in preserve mode: plan_tree.json,
plan_tree.sha256, producer_contract.json are compared against themselves

**`file_line` (verbatim):** `configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py:1803-1813,1987-1998
(7B :2185-2193, contrast :1683-1697)`

**failure_scenario (verbatim):**
> With PRESERVE_CURRENT_FROZEN_BYTES true (the current state of all three frozen packs),
> generate() echoes the on-disk plan_tree.json/plan_tree.sha256/producer_contract.json into the
> 'generated' output, so --check's regeneration-drift comparison is void for exactly the
> pack-authority root files while still printing 'verified'. Executed: a committed
> sidecar-consistent plan_tree science-row tamper passes --check AND the freeze-reference replay
> (F6); the D-134 freeze receipt binds calibration_plan, registry, and evidence but NOT plan_tree
> bytes. Remaining catches are the plan-test literal (compromised per finding 1), the off-repo
> baseline manifest, and merge review. Work order: bind a plan_tree digest at freeze (e.g., hash
> of plan_tree minus the receipt attachment, recorded in the freeze receipt or projection receipt)
> or restore genuine regeneration comparison for the frozen members of these files.

**Seat-report citation:** L5 report **line 61** (F-2) and **line 53** (falsifier F6: "Committed
`plan_tree.json` science-row tamper + regenerated sidecar | freeze-replay **PASSES** and `--check`
**PASSES**, printing the tampered sha as 'verified' (**the echo hole — finding 2**)").

### F3 — [should_fix]
**Title (verbatim):** Pre-arm sequence unregistered: measurement checkout must advance and the §5C
dry-run must be re-executed at the final head (dry-run-0001 is stale by binding)

**`file_line` (verbatim):** `RUN_STATE.md:67-70 (ED-OWED),
docs/process_traces/2026-08-13-freeze-execution/freeze-log.md (X-8),
joulewise/arm_readiness.py:3402-3425`

**failure_scenario (verbatim):**
> The measurement checkout sits at 49dcc49, which predates the arm-critical t0 evidence author
> (#149/ac3fe1d) — arming there fails immediately (script absent). After updating it,
> _latest_dry_run_binding requires the dry-run receipt to bind the CURRENT reviewed head +
> committed pack digest; dry-run-0001 binds 49dcc49/6246b618… so any arm at the baseline head
> refuses readiness_dry_run_stale (mechanically fail-closed, verified in code). Neither RUN_STATE's
> ED-OWED line ('chained ALPHA arm if GO'), the 70h plan, nor the ED-QUALIFICATION script registers
> the required steps: (1) fetch/advance the measurement checkout to the final reviewed head
> containing the t0 author, (2) re-execute the §5C under-lease dry-run there under the night's
> custody root, (3) then E-steps/t0/arm. The freeze log's X-8 wording ('the D-134 freeze + dry-run
> pair discharges the frozen readiness-validator role') invites an operator to believe the existing
> dry-run carries over; it does not.

**Seat-report citation:** L5 report **line 63** (F-3).

### F4 — [nit]
**Title (verbatim):** --check prints 'verified unfrozen draft' on frozen packs

**`file_line` (verbatim):** `configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py:149-157,2168-2171`

**failure_scenario (verbatim):**
> freeze_aware_status intentionally returns the byte-frozen legacy DRAFT_STATUS for the current
> frozen packs (M-2 byte preservation), so a frozen pack's successful check announces itself as an
> unfrozen draft — cosmetic operator-confusion risk already acknowledged by M-2 and
> alpha_arm_readiness.md.

**Seat-report citation:** L5 report **line 65** (F-4).

### F5 — [nit]
**Title (verbatim):** M-2 decision-log remedy wording diverges from the implemented preserve-bytes
behavior

**`file_line` (verbatim):** `docs/decision_log.md:8881-8891 vs docs/phase_2/alpha_arm_readiness.md:31-35`

**failure_scenario (verbatim):**
> The decision log's remedy says the chain-fix batch 'regenerates the sidecar-consistent text via
> the canonical path', which reads as regenerating the frozen packs' text; the landed behavior
> (correctly) preserves frozen bytes and applies freeze-aware wording only to future packs, as
> alpha_arm_readiness.md states. A future session acting on the decision-log wording could try to
> rewrite frozen pack bytes; consistency-sweep material.

**Seat-report citation:** L5 report **line 67** (F-5).

### Verdict interactions with L5
- **No L5 finding was struck or re-severitied.** `council-verdict.md:44-45` (Disposition 4) strikes
  L8-B4, WO-L2-4, and the L4/T-0 "F4 timing premise" — none of them L5's.
- **L5's independent finding is a mandated primary in the M-2 remand.** `council-verdict.md:36-38`
  (Disposition 2, verbatim): "M-2 will be re-submitted as its own cold-gate artifact with primaries
  attached (decision-log entry, the overridden §5C gate text, the #149 generator diff, **L5's
  independent finding**, and sweep-S3)." Corroborated by
  `opus-contract-refuter-findings.md:26` ("Absent: … and **L5's independent finding** on the packs'
  current text").
- **L5 is a named seat of the Phase-3 focused re-audit.** `council-verdict.md:102-104`:
  "**Phase 3:** baseline-manifest SUPERSESSION (with the ruled fields) + focused re-audit of
  pack/custody-bearing seats (**L1, L5, L7 minimum**) + adversarial coverage re-enumeration of all
  universes; delta re-audits per C-028 on every fix round."
- **L5's nit corroborates the cold ruling's M-2 finding:** `cold-fable-ruling.md:55` — "all three
  packs' bytes still read `\"draft_status\": \"unfrozen_draft\"` … (sweep S3; L1 nit; **L5 nit**)".

### L5 work orders, verbatim (`raw/L5-triage.md:32-38`)
- **WO-L5-1:** Port the contrast test's __pycache__ exclusion
  (tests/test_d117_decode_contrast_plan.py:59-65) to both floor-pack plan tests, add a
  pack-pollution cleanup note to the runbook pre-arm section, and pull the CI log to determine how
  the failing modules reported green (if CI was red or skipped, record the process defect in the
  council log).
- **WO-L5-2:** Close the preserve-mode --check echo hole: bind plan_tree bytes at freeze
  (receipt-side digest of plan_tree-minus-attachment, or projection-receipt-side) OR restore
  genuine regeneration comparison for the frozen packs' plan_tree/producer_contract members;
  regression-test with the F6 tamper shape.
- **WO-L5-3:** Register the pre-arm sequence in RUN_STATE ED-OWED and the runbook D-117 amendment:
  advance the measurement checkout to the final reviewed head (>= ac3fe1d, contains the t0 author),
  re-execute the §5C under-lease dry-run at that head under the night's custody root, and only then
  begin E-steps; annotate the freeze log's X-8 line with the staleness caveat.

> **Tracking fact (assembler-verified):** the identifiers `WO-L5-1` … `WO-L5-3` appear **nowhere**
> in the repository outside `docs/process_traces/2026-08-15-readiness-council/`
> (`grep -rn "WO-L5-" docs/` → `triage.json` and the two seat reports only). L5's work orders were
> never enrolled as TASK_QUEUE rows or kernel rows; the mapping below is by content.

---

## 2. WHAT CHANGED SINCE 2026-08-15

### F1 — self-polluting floor-pack plan tests

**FIX LANDED (test-side); CI-TRUTH LIMB NOT LOCATED.**
- `__pycache__` exclusion is present in both floor plan tests at `b92b43d`:
  `tests/test_d117_floor_qwen25_1p5b_plan.py` lines **40** (comment: "Loading a pack generator by
  file location writes `__pycache__` INTO the…"), **147, 312, 409, 415, 470, 1605, 1615**; and
  `tests/test_d117_floor_qwen25_7b_plan.py` lines **50, 138, 303, 459, 466, 1573, 1664** — the same
  `"__pycache__" not in path.parts` filter the contrast test carried (`test_d117_decode_contrast_plan.py:33,
  72, 158, 172, 178`).
- Commits that touched `__pycache__` in those files (`git log -S'__pycache__'`, newest first):
  `d3aa15f` (2026-08-18) "D-117 plan tests: make the successor-generation contract
  freeze-independent"; **`c94e0b0` (2026-08-18) "Post-merge integration round 2:
  freeze-transaction-shaped registry fixture + **in-pack bytecode cure**"**; `5292cf7`; `7402855`.
  The "in-pack bytecode cure" in `c94e0b0` is the identifiable carrier of WO-L5-1's first limb.
  **None of these commits names WO-L5-1**; the cure arrived inside the successor-generator stream,
  not as the council work order.
- **Executed-green evidence at the successor head:**
  `docs/process_traces/2026-08-19-refreeze-execution/s4/suite-tests.test_d117_floor_qwen25_1p5b_plan.log`
  tail: "Ran 21 tests in 5.175s / OK"; a new module `tests/test_d117_v3_family.py` exists and its
  S4 log tails "Ran 4 tests in 6.640s / OK".
- **CI-log truth determination: EVIDENCE NOT LOCATED.** The work order required pulling the CI log
  to explain how the failing modules reported green on #149, and recording a process defect in the
  council log if CI was red or skipped. Searched: `grep -rn
  "test_d117_floor_qwen25_1p5b_plan\|test_d117_floor_qwen25_7b_plan" docs/ --include=*.md` (hits
  only in the 2026-08-07 plan-factory/design-memo drafts and the council directory);
  `grep -rn "floor.*plan test\|plan-test shard\|CI log" docs/run_reports/2026-08-16-t9-session.md
  docs/council_log.md` (no post-verdict hit); `docs/council_log.md` C-058/C-059 entries (lines 92,
  93) — neither records a floor-plan-test CI determination or a process defect for it.
- **Runbook pollution-cleanup note: EVIDENCE NOT LOCATED** (searched `docs/phase_2/window_runbook.md`
  and the process docs for a pre-arm `__pycache__` cleanup step; no such note found by the greps
  above).

### F2 — preserve-mode `--check` echo hole / plan_tree unbound at freeze

**NOT CLOSED AS SPECIFIED; the surrounding state changed in ways the seat must re-examine.**
- **plan_tree is still not bound by the freeze receipt.** Assembler-verified: the string
  `plan_tree` occurs **0 times** in
  `configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json`.
  The receipt's `pack_identity` binds `plan_path: "calibration_plan.json"` + `plan_sha256:
  9ab4776f…`, not plan_tree bytes.
- **plan_tree is still not bound by the projection receipt either.** `plan_tree` occurs **0 times**
  in all three `_v3` `identity_pin_projection.receipts/projection-0001.json` (keys: `checks`,
  `derivation`, `identity_units`, `observations`, `pack`, `reason_codes`, `receipt_id`,
  `receipt_kind`, `schema_version`, `status`, `supersedes`, `work_order`).
- **No trace of the work order:** `grep -rn "echo hole\|WO-L5-\|preserve-mode --check\|plan_tree
  digest" docs/` (excluding the council directory) returns **nothing**.
- **New state that changes the preserve-mode question for `_v3`:** in
  `configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py`,
  `PRESERVE_CURRENT_FROZEN_BYTES` is computed at `:221-223` as
  `_FREEZE_REFERENCE.get("sha256") == CURRENT_FROZEN_RECEIPT_SHA256`, and
  `CURRENT_FROZEN_RECEIPT_SHA256` (`:75-77`) is **`1277103b…`** — the **`_v2` freeze-0002** sha —
  while the `_v3` plan_tree's `arm_attachments.arm_readiness.freeze_receipt` now binds
  `arm_readiness.freeze.receipts/freeze-0003.json`, sha **`0abfddb1…`**. On its face the predicate
  is now **false** for the `_v3` packs, i.e. the echo path is not the active path there — but the
  same constant drives `freeze_aware_status` (`:190`), which is F4's mechanism. **Not verified by
  execution** (running `--check` in this tree would itself write `__pycache__` into a frozen pack —
  the F1 defect — and the tree is read-only).
- **Also new:** the `_v3` plan_tree attachment now carries
  `"pack_digest_algorithm": "joulewise.committed_pack_tree_sha256.v1"`, and the freeze-0003
  `predecessor` block carries the same key — the algorithm identifier the verdict requires in the
  *manifest* (`council-verdict.md:68-70`) is present in the *pack*, but see the manifest item in
  ROW-L1 §2.

### F3 — pre-arm sequence / stale dry-run binding

**PARTIALLY OVERTAKEN BY EVENTS; the core condition is UNCHANGED and now applies to a new family.**
- **A new measurement checkout exists and is advanced:** `/Users/edr/JouleWise-measurement-20260818`
  on branch `impl/r2-s0-mint-resolver`, head **`94dc3b34`** (the third freeze-0003 commit) — well
  past `ac3fe1d`, so it does contain the t0 author. The old checkout
  `/Users/edr/JouleWise-measurement-20260813` is still at **`49dcc49`** ("FREEZE 6/6: D-134 freeze
  receipt — GAMMA PASS…"), exactly as L5 recorded.
- **But the advanced checkout is itself 10 commits behind the branch head**
  (`git rev-list --count 94dc3b34..HEAD` = **10**: `8b2b021`, `75cb868`, `881e1bd`, `0e96dbb`,
  `c00c7bb`, `f8a8fef`, `d10881b`, `79a4cd0`, `4597ad4`, `b92b43d`), so the "advance to the final
  reviewed head" step is still owed at arm time.
- **The §5C dry-run is still the stale 2026-08-13 one, and it is for a retired pack.**
  Assembler-listed `~/JouleWise-window-custody/`: the only dry-run receipt in external custody is
  `~/JouleWise-window-custody/d117_floor_qwen25_1p5b_v1/arm_readiness.dry_run.receipts/dry-run-0001.json`
  (+ `.sha256`). There is **no custody directory for any `_v3` pack**, hence **no dry-run at any
  head containing the t0 author**, and none for the family that would actually be armed.
- **No arm or consumption receipts exist anywhere in custody** (consistent with "arming hasn't
  happened"; L5 report line 38 said the same on 2026-08-15).
- **Registration of the pre-arm sequence: PARTIAL / DIFFERENT SHAPE.** `RUN_STATE.md` no longer
  carries the old ED-OWED pre-arm text at :67-70; the live surfaces instead carry the D-149
  auto-GO regime — `docs/decision_log.md:172` (D-149, five mechanical T-0 conditions incl. "(2) the
  frozen pack's arm ceremony passes every gate with **freshness horizons honored**") and new
  operator artifacts `docs/process/d149-go-receipt-template.md` (commit `79a4cd0`) and the
  shakedown-v3 first-light run card (`b92b43d`). **A registered step-by-step "advance checkout →
  re-execute §5C dry-run at the final head → then E-steps" sequence was not located** in
  `RUN_STATE.md` or `docs/phase_2/window_runbook.md` by the greps run (`ED-OWED`, `measurement
  checkout`, `dry.run`, `pre-arm` over RUN_STATE.md; `arm_readiness.t0.inputs` over the runbook).
- **Freeze-log X-8 annotation: EVIDENCE NOT LOCATED** (no post-verdict edit to
  `docs/process_traces/2026-08-13-freeze-execution/freeze-log.md` was found by the WO-L5 greps).

### F4 — `--check` prints "verified unfrozen draft" on frozen packs

**RECURS VERBATIM ON THE SUCCESSOR FAMILY (executed evidence in custody).**
`docs/process_traces/2026-08-19-refreeze-execution/s4/check-preauthor-1p5b_v3.log`, last line
(verbatim): "verified **d117_floor_qwen25_1p5b_v3 unfrozen draft**: 100 science configs;
calibration_plan_sha256=9ab4776f3c416284d6d01a5a49587eedcdfbcb8ef61428cdc1046e9b9d74a072;
plan_tree_sha256=628ad9d8d6b3e1fb82699a90ba7833181f161e1683878a9a8fb41ca5850448e5".
Separately, `docs/process/state_kernel.json` and the `_v2`/`_v3` plan trees **no longer carry a
`draft_status` key at all** (only `_v1` does, at `plan_tree.json:793`), so the *byte* form of the
nit is family-scoped to `_v1` while the *printed* form recurs on `_v3`.
Also in that custody dir: `check-d117_floor_qwen25_1p5b_v3.log` ends "generation failed: pack
inventory differs: extras=arm_readiness.evidence/…, arm_readiness.sources/…" — after S4 evidence
authoring the `_v3` generator `--check` **fails on inventory**, i.e. the `--check` catch layer's
current behaviour on the successor family is materially different from what L5 audited.

### F5 — M-2 decision-log wording vs implemented preserve-bytes behaviour

**RULED, NOT YET RETIRED.** The M-2 remand is Disposition 2 (`council-verdict.md:33-40`);
`cold-fable-ruling.md:55` ruled the remedy "**AS ENGINEERING, YES; AS RECORDED, NO**" and required
(a) an M-2 execution note in the decision log and (b) truthful freeze-aware status text from the
re-freeze, "at which point the M-2 override retires". Post-verdict record located:
`docs/process_traces/2026-08-18-freeze-semantics-coldgate/` (14 files incl. `05-m2-decision-log-excerpt.txt`,
`12-cold-adjudicator-ruling.md`, `13-opus-contract-refuter.md`, `14-composed-verdict.md`), whose
composed verdict holding 2 (verbatim, lines 24-30) states: "**Fresh doctrine extension, not
precedent citation** … this verdict itself EXTENDS the receipts-govern-over-descriptive-bytes core
to ALL successor packs by dated decision-log entry (**to be minted at the merge gate**), on the
authority of this gate's executed evidence. The M-2(b) informational operator note gets a runsheet
row before the arm gate." Decision-log rows **D-140/D-141** (freeze-status byte semantics;
generator write-boundary residuals) are the recorded outcome. **The merge gate has not happened**,
so the "to be minted at the merge gate" entry and the retirement of M-2 are both still pending, and
the F4 evidence above shows the untruthful status text recurring on `_v3`.

### The successor family, receipts, U11 projections, custody, and the S5 confirmation table

Commits (all ancestors of `b92b43d`; subjects verbatim from `git log`):

| Commit | Subject |
|---|---|
| `1d3873b` | S3: d117 _v3 pack family emitted via unedited _v2 generators, bound to r6 at birth; family tests (successor emission, replay integrity, byte preservation) |
| `3d05982` | D-147 S5/U11: identity-pin projection frozen for d117_floor_qwen25_1p5b_v3 (projection-0001, 2 units, PASS) |
| `6fd8bce` | D-147 S5/U11: identity-pin projection frozen for d117_floor_qwen25_7b_v3 (projection-0001, PASS) |
| `74632e3` | D-147 S5/U11: identity-pin projection frozen for d117_contrast_qwen25_1p5b_vs_7b_v3 (projection-0001, PASS) |
| `5e38f1e` | D-147 S5: freeze-0003 minted for d117_floor_qwen25_1p5b_v3 (PASS; predecessor _v2/freeze-0002 1277103b…; receipt 0abfddb1…) |
| `eb7f6c6` | D-147 S5: freeze-0003 minted for d117_floor_qwen25_7b_v3 (PASS; predecessor _v2/freeze-0002 decd8cdc…) |
| `94dc3b3` | D-147 S5: freeze-0003 minted for d117_contrast_qwen25_1p5b_vs_7b_v3 (PASS; predecessor _v2/freeze-0002 18855647…) |
| `8b2b021` | S5 COMPLETE: confirmation table filled (three freeze-0003 receipts + committed tree digests) |

**Assembler-executed verification at `b92b43d` (read-only):**
- **Freeze receipts:** all three `freeze-0003.json` are `status: PASS`, 14 rows, `refusals: []`,
  with a `predecessor` block naming the `_v2` `freeze-0002.json`, its sha, the predecessor
  `identity_receipt`, `evidence_set_sha256`, and `pack_digest_algorithm:
  joulewise.committed_pack_tree_sha256.v1`. Issued at 2026-08-20T00:27:50Z / 00:2x (UTC).
- **Committed pack tree digests recomputed with the project's own
  `joulewise.arm_readiness.committed_pack_tree_sha256`: all three MATCH** the S5 confirmation
  table — `1e3f1fa3…` (1p5b_v3), `6d0b9b75…` (7b_v3), `0d071941…` (contrast_v3).
- **U11 projections:** all three `projection-0001.json` are `status: PASS`, `supersedes: []`, with
  populated `checks[].expected`/`observed` model/config/runtime shas (real model bytes) and
  `pack.reviewed_git_commit: d59d36f50098c343af642a6bc24259247469d5a9`.
- **Evidence:** 11 receipts per `_v3` pack (33 total), each
  `schema_version: joulewise.arm_readiness_evidence_receipt.v1`, `boot_session_id:
  da90818c-9c31-45d0-8813-deae65fba143`, `head_commit: 1d3873bb…`, and a top-level
  `valid_until_monotonic_ns`. Live `sysctl -n kern.bootsessionuuid` at probe time matched
  (`DA90818C-…`). Minimum `valid_until_monotonic_ns` = `2468742407178458` vs live
  `CLOCK_UPTIME_RAW` = `2414989316822250` → **≈14.9 h headroom at probe time**;
  `RUN_STATE.md:210-212` states the same deadline in prose ("EXPIRES ~2026-08-20T16:51Z … DIES ON
  ANY REBOOT").
- **S5 confirmation table (`8b2b021`), `docs/process/ed-s5-mint-decision-2026-08-19.md:71-85`,
  header verbatim:** "## Confirmation table (COMPLETE — S5 executed 2026-08-19 under D-148.1,
  mints via Ed-approved manual prompts)" — rows include the live acceptance generation
  `d079_calibration_acceptance_v2_n17_r6` (sha `0227bca3…`), the three `_v2` freeze-0002
  predecessor shas, the S4 evidence rollups (`0e353456…` / `1421ea4e…` / `653f22c0…`), and the
  three freeze-0003 shas + committed tree digests. **Ed's exact-byte confirmation is still owed**
  (`:94-95`: "final exact-byte publication confirmation (this table, post-mint)").
- **External custody state:** `~/JouleWise-window-custody/` contains 19 entries; relevant ones are
  `d117_floor_qwen25_1p5b_v1/` (the single stale `dry-run-0001`), `ed-qual-20260817/`,
  `shakedown-20260818/`, `profiler-pilot-20260818/`, `t4-session-20260810/` (the arm-packet
  document L5 located but did not audit). **No `_v3` custody root, no dry-run, arm, or consumption
  receipt for the successor family.**

### Phase 3's required FOCUSED RE-AUDIT of L5

**DOES NOT EXIST.** `ls docs/process_traces/ | grep 2026-08-1[5-9]` returns 22 directories; the
only re-audit among them is `2026-08-15-l2-reaudit` (the Phase-1 WO-L2-REAUDIT, TASK_QUEUE.md:103).
No artifact for a focused L1/L5/L7 re-audit was located, and the manifest supersession that Phase 3
sequences it after has not been cut (see ROW-L1 §2).

---

## 3. ED-QUALIFICATION ROWS

Charter rule in force: `council-verdict.md:54-57` — READY-CANDIDATE sittings bind charter 77-78,
"only T0 rows may remain open".

> **Tracking fact:** `ED-QUAL-L5-1` appears **nowhere outside**
> `docs/process_traces/2026-08-15-readiness-council/` (`triage.json`,
> `sitting-packet-FINAL.md:180`, the L5 seat report). Searched additionally: `RUN_STATE.md`,
> `TASK_QUEUE.md`, `docs/process/state_kernel.json`, `docs/phase_2/ed-qualification-session.md`,
> `docs/process/ed-batch-packet.md`, `docs/process/ed-evening-checklist.md`,
> `docs/process/ed-morning-packet-2026-08-18.md`, `docs/run_reports/2026-08-18-t10-session.md`.
> No closure ledger exists.

### ED-QUAL-L5-1
**Row text VERBATIM (`raw/L5-triage.md:42`):**
> ED-QUAL-L5-1 (stable capability, any tap block): one non-window rehearsal of the t0
> clock-attestation input handshake — Ed captures real `sudo systemsetup -getusingnetworktime` /
> `-setusingnetworktime off` outputs per runbook E-4/E-5 into a scratch arm_readiness.t0.inputs
> namespace and the lead validates them against the t0 author's capture validators
> (joulewise/arm_readiness_evidence_t0.py:838-861 _systemsetup_argv / _derive_clock_attestation).
> The authored tests use synthetic captures only; the first real sudo-output shape mismatch must
> not surface at T-0.

**Kind:** declares itself **stable capability** ("any tap block") — **not** a T0/perishable row, so
the charter's T0 exemption does not reach it.

**LOCATED CLOSURE EVIDENCE — PARTIAL: the raw captures exist; the namespace and the validator
check do not.**
- **Real `systemsetup` outputs WERE captured on the production Mac** during the T10 qualification
  evening. Custody `~/JouleWise-window-custody/ed-qual-20260817/`, assembler-read verbatim:
  - `sudoers-vector-off.txt`: an `### Error:-99 … InternetServices.m Line:395` line followed by
    `setUsingNetworkTime: Off`
  - `sudoers-vector-on.txt`: same error line followed by `setUsingNetworkTime: On`
  - `clock-prior-state.txt` / `clock-post-state.txt` / `vector-on-confirmed.txt`:
    `Network Time: On`
  This is exactly the real-output-shape material the row exists to surface — including the
  **stderr `### Error:-99` prefix line**, which is precisely the "first real sudo-output shape
  mismatch" hazard the row names.
- **Recorded as closed under a different row.** `docs/run_reports/2026-08-18-t10-session.md:104`
  (verbatim): "| **D-127 sudoers** | Installed root:wheel 0440; digest **`7dfe980b…`** verified;
  **both** vectors passwordless with ground-truth state flips (Network Time Off→On) |
  `sudoers-digest.txt`, `sudoers-vector-{on,off}.txt`, `vector-{on,off}-confirmed.txt`,
  `clock-{prior,post}-state.txt` |". The report's summary line (`:5-6`) claims "**every stable
  qualification row closed with custody evidence**", but its table (`:102-110`) lists D-127
  sudoers, sampler lifecycle, rail probe, backlight, ED-QUAL-L4-1, ED-Q-L9-3, and **dress rehearsal
  = OPEN** — **ED-QUAL-L5-1 is not a row in that table**.
- **NO EVIDENCE LOCATED that the captures were written into an `arm_readiness.t0.inputs` namespace,
  nor that the lead validated them against `arm_readiness_evidence_t0.py:838-861`.** Searched:
  `grep -rn "arm_readiness.t0.inputs" docs/ --include=*.md` (hits only in `council_log.md:3582`,
  `decision_log.md:9885`, `window_runbook.md:883,978,1020`, and the council packet/seat reports —
  none an execution record); `find ~/JouleWise-window-custody -maxdepth 3 -name "*t0*"` → **no
  results**; `grep -rn "clock-attestation\|clock attestation"
  docs/run_reports/2026-08-18-t10-session.md docs/process/ed-*.md` → **no results**.
- **Feasibility changed in the row's favour:** the producer the row's handshake needs now exists —
  TASK_QUEUE.md:106 (WO-T0-PRODUCER, verbatim): "Merged via #152 (`a61ac92`) at D-121-verified head
  `9e8936a`: `scripts/capture_t0_step.py`, the strict R2 plan resolver, the D-127 privileged clock
  route, and dwell/env hardening landed". The rehearsal is therefore executable now in a way it was
  not on 2026-08-15.
- **The related dress rehearsal (author→arm→verify→consume vs scratch custody), which would
  subsume this handshake, is recorded OPEN:** `docs/run_reports/2026-08-18-t10-session.md:110` —
  "| **Dress rehearsal** | **OPEN** — gated on the frozen `_v2` alpha pack, i.e. on Ed's item-1
  ruling | morning packet §4 |". No later artifact showing it was executed was located.

---

## 4. CANDIDATE DISPOSITIONS FOR THE SEAT TO ADJUDICATE

Candidate dispositions are assembled, not adjudicated; the seat rules.

| Item | Candidate disposition |
|---|---|
| **F1** — self-polluting floor-pack plan tests; CI-green unexplained | **STILL-OPEN (split).** Limb 1 (the `__pycache__` exclusion) is **READY-evidence-attached**: filters present in both floor tests at HEAD, carried by `c94e0b0` "in-pack bytecode cure" (2026-08-18), with S4 custody logs showing 21/21 and 4/4 OK. Limb 2 (**pull the CI log; record the process defect if CI was red or skipped**) — **EVIDENCE NOT LOCATED**. Limb 3 (runbook pack-pollution cleanup note) — **EVIDENCE NOT LOCATED** |
| **F2** — preserve-mode `--check` echo hole; plan_tree unbound at freeze | **STILL-OPEN.** Neither remedy was executed under its work order: freeze-0003 binds no `plan_tree` (0 occurrences), the projection receipt binds none either, and no repo trace of the work order exists. Changed context the seat must re-audit: for `_v3`, `PRESERVE_CURRENT_FROZEN_BYTES` compares the plan-tree attachment sha (`0abfddb1…`, freeze-0003) against a constant still set to the `_v2` `1277103b…`, so the preserve path's current behaviour on the successor family is **unverified by execution** |
| **F3** — pre-arm sequence unregistered; dry-run stale by binding | **STILL-OPEN.** A new advanced measurement checkout exists (`…-20260818` @ `94dc3b34`) but is 10 commits behind HEAD; the only external dry-run receipt remains `dry-run-0001` bound to `49dcc49` and to the retired `_v1` ALPHA pack; **no `_v3` custody root or dry-run exists**; the step-by-step registration and the freeze-log X-8 annotation were not located. Note the regime change: D-149 now auto-issues T-0 GO on five mechanical conditions, which raises rather than lowers the bar for having this sequence registered mechanically |
| **F4** — `--check` prints "verified unfrozen draft" | **STILL-OPEN, RECURRED.** Executed custody evidence at the successor head: `check-preauthor-1p5b_v3.log` prints "verified d117_floor_qwen25_1p5b_v3 **unfrozen draft**". Nit-severity, but it is the operator-facing symptom the re-freeze was supposed to retire |
| **F5** — M-2 wording vs implemented behaviour | **STILL-OPEN (ruled, not executed).** M-2 remanded (Disposition 2) and materially advanced by the 2026-08-18 freeze-semantics cold gate (D-140/D-141); its composed verdict defers the dated decision-log entry to the merge gate, which has not occurred. M-2 does not retire until truthful freeze-aware status text ships — and F4 shows it has not |
| **Baseline-manifest supersession + Phase-3 focused re-audit of L5** | **STILL-OPEN — not started.** No re-audit artifact exists; the manifest is unsuperseded and its `_v1` pack digests no longer reproduce at HEAD (see ROW-L1 §2) |
| **U17 / U18 (the two uncovered universe classes)** | **STILL-OPEN.** U17 (CI behaviour of the pack-integrity plan tests) — no determination located. U18 (live arm-night chain: dry-run at final head, t0 author, arm/verify/consume, U11 live verify) — no arm or consumption receipt exists in any custody root |
| **ED-QUAL-L5-1** (stable capability) | **ED-ROW OPEN.** Real `systemsetup` captures exist in `ed-qual-20260817/` (including the `### Error:-99` stderr shape), but no `arm_readiness.t0.inputs` namespace and no validation against `arm_readiness_evidence_t0.py:838-861` were located; the row is not a line item in the T10 qualification table; the subsuming dress rehearsal is recorded OPEN |
| **PER-SEAT OVERALL** | **CANDIDATE: NOT-READY-as-assembled.** One of three work orders is substantially delivered (F1 limb 1, with its CI-truth limb unmet); F2 and F3 are unexecuted under their own terms and now apply to a *different pack family* than the one L5 audited; both nits persist and F4 recurs with executed evidence at the successor head; the seat's two uncovered universe classes (U17, U18) are still uncovered; Phase 3's mandated focused re-audit of this very seat has not been performed; and the ED row lacks the validator-side closure its own text requires. The seat rules |

---

## 5. WHAT A SKEPTICAL SEAT SHOULD PROBE

1. **(a) Stale-head attack.** Compare every head in the L5 evidence chain to the tree head.
   `git -C <wtS0> log --oneline -1` → `b92b43d` (brief says `4597ad4`).
   `git -C /Users/edr/JouleWise-measurement-20260818 log --oneline -1` → `94dc3b34`;
   `git -C <wtS0> rev-list --count 94dc3b34..HEAD` → **10**. `_v3` evidence binds `head_commit
   1d3873bb…`; `_v3` U11 projections bind `reviewed_git_commit d59d36f5…`.
   **Falsifier:** `joulewise/arm_readiness.py::_latest_dry_run_binding` requires the dry-run to
   bind the CURRENT reviewed head + committed pack digest — so an arm attempted at `b92b43d` with
   only `dry-run-0001` (bound to `49dcc49` and `6246b618…`) refuses `readiness_dry_run_stale`,
   which is F3 unrepaired, verbatim, on a new family.
2. **(b) Coverage / universe re-enumeration attack (standing packet element,
   `council-verdict.md:18-22`).** Do not accept 18 classes. Re-enumerate: the `_v3` family adds
   three packs (U1–U3 analogues), three freeze-0003 receipts, three U11 projection receipts, 33
   evidence receipts + 33 sources + sidecars, three `_v3` generators, plus the `_v2` family
   (nine more pack-shaped classes total) and the new `tests/test_d117_v3_family.py`.
   **Falsifier:** if the honest denominator is now ~27+ and the numerator has not moved, L5's
   16/18 is a self-nominated denominator of the exact kind that felled L2.
3. **(c) Self-reported repair with no independent audit — S4/S5.** Every claim that the `_v3`
   receipts were verified traces to the implementing session
   (`RUN_STATE.md:169-171`; `docs/process/ed-s5-mint-decision-2026-08-19.md:66-69`;
   `docs/run_reports/2026-08-19-t12-t13-session.md`). Enumerate
   `docs/process_traces/2026-08-19-refreeze-execution/reports/` and check whether an **S4 or S5**
   lens/delta report exists at all (the assembler saw S0/S1 lens+delta, S2 goldens, S3 emission,
   consistency sweep, docs-fidelity — no S4/S5 audit). Cross-check `RUN_STATE.md:146-149` (the
   **D-144 BIG-design pre-merge seat pass over the implemented S0–S5 artifact has not run**;
   "POOL-GATED… a ruled requirement of D-146/D-147's own classification, not optional") and
   `RUN_STATE.md:133-135` ("**BOTH GATE INPUTS ARE UNSATISFIED** and must be rerun from scratch").
   **Falsifier:** the successor family that this seat is being asked to bless has no independent
   audit and no completed pre-merge seat pass.
4. **F2, executed — re-run the F6 tamper on the `_v3` family, in a disposable clone.** Copy a
   `_v3` pack into a scratch git repo, commit a `plan_tree.json` science-row tamper with a
   regenerated sidecar, then run the generator `--check` and the freeze-reference replay.
   **Do NOT run `--check` inside `wtS0`** — it writes `__pycache__` into a frozen pack (F1) and the
   tree is read-only. **Falsifier:** if `--check` prints "verified" on the tampered plan_tree, or
   if the freeze-0003 replay passes it, the echo hole survives into the family that will actually
   be armed — and the manifest catch layer L5 relied on is gone (the manifest is stale; ROW-L1 §2).
5. **F2 predicate check, statically.** Read
   `configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:75-77, 190, 221-223` and
   compare `CURRENT_FROZEN_RECEIPT_SHA256` (`1277103b…`, a `_v2` freeze-0002 sha) with the `_v3`
   plan_tree attachment sha (`0abfddb1…`, freeze-0003). **Falsifier:** the constant was not
   retargeted at the S5 freeze, so `freeze_aware_status` and the preserve predicate both key off a
   predecessor family's receipt — which is either a latent status-text lie or a latent
   regeneration-drift failure, and the custody logs show both symptoms
   (`check-preauthor-1p5b_v3.log` "unfrozen draft"; `check-d117_floor_qwen25_1p5b_v3.log`
   "generation failed: pack inventory differs").
6. **F1's CI limb, mechanically.** Read `.github/workflows/ci.yml`'s shard discovery (lines ~51-59
   use `shard_tests.discover_test_modules()`), determine whether
   `tests.test_d117_floor_qwen25_{1p5b,7b}_plan` and `tests.test_d117_v3_family` are in the
   discovered set or in the exclusive/excluded set, then pull the actual Actions log for the head
   under review. **Falsifier:** if the modules are excluded or were never green in hosted CI, the
   pack-integrity literal-pin catch layer is still not real — and neither the council log nor any
   run report records the process defect the work order demanded.
7. **F3, custody-side.** `ls -R ~/JouleWise-window-custody/` and confirm there is no
   `<custody_root>/d117_*_v3/arm_readiness.dry_run.receipts/` and no arm/consumption receipt
   anywhere. **Falsifier:** the §5C under-lease dry-run for the family that would be armed does not
   exist at any head, so the pre-arm sequence F3 named is not merely unregistered — it is
   unperformed.
8. **ED-QUAL-L5-1's actual ask.** Read `joulewise/arm_readiness_evidence_t0.py:838-861`
   (`_systemsetup_argv` / `_derive_clock_attestation`) and feed it the real captured bytes in
   `~/JouleWise-window-custody/ed-qual-20260817/sudoers-vector-{on,off}.txt` and
   `clock-{prior,post}-state.txt` — note the stderr line `2026-08-17 17:56:53.240
   systemsetup[80364:158022551] ### Error:-99 …` that precedes `setUsingNetworkTime: On`.
   **Falsifier:** if the validator rejects (or silently mis-parses) that real two-line shape, the
   row's stated hazard — "the first real sudo-output shape mismatch must not surface at T-0" — is
   live and unclosed despite the captures existing.
9. **Freshness horizon at sitting time (shared with L1-B1, but it lands on this seat's custody
   chain).** Recompute min `valid_until_monotonic_ns` across `configs/campaigns/*_v3/arm_readiness.evidence/*.json`
   against live `CLOCK_UPTIME_RAW`, and confirm `sysctl -n kern.bootsessionuuid` still equals
   `da90818c-…`. Assembler measurement: ≈14.9 h headroom; stated death ~2026-08-20T16:51Z or any
   reboot. **Falsifier:** if the sitting concludes after that horizon, the pack chain this row
   documents is already unarmable and the whole custody argument must be re-made on re-authored
   evidence.
10. **M-2 retirement precondition.** Check whether the dated decision-log entry the freeze-semantics
    composed verdict defers "to be minted at the merge gate"
    (`docs/process_traces/2026-08-18-freeze-semantics-coldgate/14-composed-verdict.md`, holding 2)
    has been minted, and whether the M-2(b) operator note has a runsheet row in
    `docs/process/phase2-transaction-runsheet.md` before the arm gate. **Falsifier:** if neither
    exists and no merge has occurred, M-2 is still the operative instrument, which is exactly what
    `cold-fable-ruling.md:55` called "an override that quietly converts from transitional to
    permanent without a recorded decision".

---

## 6. OPEN ITEMS FROM THIS ROW

- **Phase 3's mandated focused re-audit of L5 does not exist** (`council-verdict.md:102-104`
  names L1/L5/L7 minimum); the only post-verdict re-audit artifact in `docs/process_traces/` is
  `2026-08-15-l2-reaudit`.
- **WO-L5-1's CI-truth limb is unmet: EVIDENCE NOT LOCATED.** Searched
  `grep -rn "test_d117_floor_qwen25_1p5b_plan\|test_d117_floor_qwen25_7b_plan" docs/ --include=*.md`;
  `grep -rn "floor.*plan test\|plan-test shard\|CI log" docs/run_reports/2026-08-16-t9-session.md
  docs/council_log.md`; the C-058/C-059 council-log entries. No CI-log determination and no
  recorded process defect.
- **WO-L5-1's runbook pack-pollution cleanup note: EVIDENCE NOT LOCATED.**
- **WO-L5-2 (echo hole / plan_tree binding at freeze) is unexecuted:** freeze-0003 contains zero
  `plan_tree` references; the U11 projection receipts contain zero; no repo trace of the work order
  exists.
- **The `_v3` generators' `CURRENT_FROZEN_RECEIPT_SHA256` still names the `_v2` freeze-0002 sha
  (`1277103b…`) while the `_v3` attachment binds freeze-0003 (`0abfddb1…`)** — the preserve/status
  predicate keys off a predecessor family's receipt; current behaviour unverified by execution.
- **WO-L5-3 is unexecuted as specified:** no registered "advance checkout → re-execute §5C dry-run
  at the final head → then E-steps" sequence located in `RUN_STATE.md` or
  `docs/phase_2/window_runbook.md`; **no freeze-log X-8 staleness annotation located.**
- **No §5C dry-run exists for the `_v3` family at any head**; the only external dry-run receipt is
  `~/JouleWise-window-custody/d117_floor_qwen25_1p5b_v1/arm_readiness.dry_run.receipts/dry-run-0001.json`,
  bound to `49dcc49` and to a retired pack. **No arm or consumption receipt exists anywhere in
  custody.**
- **The advanced measurement checkout `/Users/edr/JouleWise-measurement-20260818` (`94dc3b34`) is
  10 commits behind the branch head**, so the "advance to the final reviewed head" step is still
  owed at arm time; the old checkout `…-20260813` is still at `49dcc49`.
- **F4 recurs on the successor family with executed evidence:**
  `docs/process_traces/2026-08-19-refreeze-execution/s4/check-preauthor-1p5b_v3.log` prints
  "verified d117_floor_qwen25_1p5b_v3 **unfrozen draft**".
- **Post-S4, the `_v3` generator `--check` fails on inventory** ("generation failed: pack inventory
  differs: extras=arm_readiness.evidence/…, arm_readiness.sources/…",
  `s4/check-d117_floor_qwen25_1p5b_v3.log`) — the `--check` catch layer's behaviour on the family
  to be armed is materially different from what L5 audited and has not been re-audited.
- **F5 / M-2 is ruled but not retired:** the dated decision-log entry is deferred "to be minted at
  the merge gate" (freeze-semantics composed verdict, holding 2) and no merge has occurred.
- **Both of L5's uncovered universe classes remain uncovered:** U17 (CI behaviour of the
  pack-integrity plan tests) and U18 (live arm-night chain incl. U11 `verify_frozen_projection`
  with real model bytes).
- **The seat's other unexecuted obligations are unchanged:** `identity_pins.py` internals not
  line-read; the arm-packet document under `~/JouleWise-window-custody/t4-session-20260810/`
  located but not content-audited.
- **ED-QUAL-L5-1 is open:** real `systemsetup` captures exist in
  `~/JouleWise-window-custody/ed-qual-20260817/` (including the `### Error:-99` stderr prefix), but
  **no `arm_readiness.t0.inputs` namespace and no validation against
  `arm_readiness_evidence_t0.py:838-861` were located** (searched the runbook, the T10 report, the
  Ed packets, and `find ~/JouleWise-window-custody -name "*t0*"` → no results). The row is absent
  from the T10 qualification table, and the subsuming dress rehearsal is recorded **OPEN**
  (`docs/run_reports/2026-08-18-t10-session.md:110`).
- **`WO-L5-1` … `WO-L5-3` were never enrolled** as TASK_QUEUE or kernel rows; there is no
  per-work-order closure record for this seat.
- **No independent audit of the S4/S5 execution was located**, and the ruled D-144 pre-merge seat
  pass over the implemented S0–S5 artifact has not run; both merge-gate inputs are recorded
  UNSATISFIED (`RUN_STATE.md:133-135, 146-149`).
- **Nothing has merged to main** (`RUN_STATE.md:138`), so every repair above lives only on
  `impl/r2-s0-mint-resolver`.
- **Provenance discrepancy:** the assembler brief states HEAD `4597ad4`; the tree is `b92b43d`.

---

## 7. ADDENDUM — the read-only tree MOVED during assembly (recorded, not graded)

All verifications in §§1–6 were executed at **`b92b43d`**. At the close of assembly the shared
worktree had advanced to **`48f337b`** (three commits later; a concurrent writer landed during
assembly): `7305e0d` (prep-sprint paper staging), `45e0229` ("Fresh-pass gate CLEAN through
b92b43d (report custodied); fix its B1/B2 + S1-S10 bookkeeping findings…"), `48f337b` (README
freshness-owner pointer restore).

**What this changes for L5 (verified by `git diff b92b43d..HEAD`):**
- **Unchanged:** every `configs/campaigns/**` byte (all three `_v3` packs, their freeze-0003
  receipts, U11 projections, and 33 evidence receipts), `docs/process/audit-baseline-manifest.json`,
  `tests/test_d117_floor_qwen25_{1p5b,7b}_plan.py`, `tests/test_d117_v3_family.py`,
  `docs/phase_2/window_runbook.md`, and all custody roots under `~/JouleWise-window-custody/`.
  Every §2 finding-level conclusion therefore still holds at `48f337b`.
- **Changed and L5-adjacent:** `docs/process/state_kernel.json` — the three window rows' `goal`
  fields now name the `_v3` packs (was `_v1`) and their `status_note` was shortened to "Successor
  family frozen (freeze-0003, 2026-08-19); awaits READY-candidate council + D-149 GO conditions",
  **dropping the prior explicit Phase-2 re-freeze / Phase-3 re-audit fence language**. Also
  changed: `RUN_STATE.md`, `TASK_QUEUE.md`, `WINDOW_STATUS.md`, `README.md`, one line of
  `docs/decision_log.md`, one line of `tests/test_gen_state.py`.
- **New custody file relevant to ROW-L5 §5 probe 3:**
  `docs/process_traces/2026-08-19-prep-sprint/merge-freshpass.md` (350 lines) claims the fresh-pass
  merge-gate input is **CLEAN through `b92b43d`** — the input `RUN_STATE.md:133-135` recorded as
  UNSATISFIED. The seat should read it directly and establish (i) whether it examined the S4/S5
  pack/custody artifacts at all, (ii) whether it is independent of the implementing session, and
  (iii) that its coverage necessarily stops at `b92b43d`, excluding `45e0229` and `48f337b`.
- **Still true after the move:** no `_v3` custody root, no dry-run at any head containing the t0
  author, no arm or consumption receipt anywhere, and no Phase-3 focused re-audit of L5.
