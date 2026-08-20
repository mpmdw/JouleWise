# ROW L1 — AUTHORITY PLANE (gating seat, xhigh tier)

> **Assembler note on the tree actually read.** The assembler brief names HEAD
> `4597ad4`. The read-only worktree
> `/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtS0`
> is on branch `impl/r2-s0-mint-resolver` at **`b92b43d`** ("Shakedown-v3 first-light run card
> (prep item 6b)…"), one commit AHEAD of `4597ad4` (`4597ad4` verified an ancestor of HEAD).
> Every "current head" statement in this row is at **`b92b43d`**. The branch is NOT merged to
> main (RUN_STATE.md:138 — "NO MERGE HAS OCCURRED").

## 0. Seat identity and 2026-08-15 result

- **Seat:** `L1-AUTHORITY-PLANE`, gating, xhigh.
- **Seat verdict as recorded:** **NOT_READY** (`raw/L1-triage.md:6`; seat report §6, line 92:
  "## 6. Verdict: **NOT-READY** (component: authority plane), with work orders").
- **Coverage:** **20 / 24** (`evidence_universe_count = 24`; `raw/L1-triage.md:7`; seat report
  §2 line 38: "**20 of 24** items examined (2 partial: identity_pins internals, evidence_t0
  internals; 2 not read: arm_readiness_evidence.py line-level,
  reserve_calibration_window_bracket.py)").
- **Findings:** 8; **falsifiers:** 7 (`raw/L1-triage.md:8`); seat report §3 records "fifteen
  executed" negative/READY-falsification probes (line 56).
- **Sitting verdict:** `docs/process_traces/2026-08-15-readiness-council/council-verdict.md`
  **lines 10–16** — "**NOT-READY. 0 READY / 11 NOT-READY**… **No funded window may be armed.**"
  Standing caution at **lines 18–22**: "**The work-order program is NOT CERTIFIED COMPLETE**…
  Closing all listed work orders does not entitle READY".
- **Seat report path:**
  `docs/process_traces/2026-08-15-readiness-council/seat-reports/L1-AUTHORITY-PLANE-report.md`
  (107 lines).
- **Seat's own audit-baseline note (report line 4):** manifest HEAD
  `ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b`; worktree head at audit time `8937dec`.

---

## 1. FINDINGS — original text verbatim, with citation

### F1 — [blocker] (seat label **B1**)
**Title (verbatim):** Frozen packs cannot arm: all 33 freeze evidence receipts have lapsed their
monotonic validity on the un-rebooted arming machine

**`file_line` (verbatim):** `configs/campaigns/*/arm_readiness.evidence/*.json;
joulewise/arm_readiness.py:3710-3717,3948-3955`

**failure_scenario (verbatim):**
> Ed attempts tonight's slipped Window ALPHA arm: generate_arm_receipt authenticates the pack
> freeze evidence (boot session matches — no reboot occurred), but the arm receipt's valid_until
> is min-inherited from evidence expirations that are already in the past (earliest
> 1986799611717708 ns vs live ~1997.9e12 ns), so verify_arm_receipt refuses
> readiness_record_expired and consume_launch_capability can never fire. The direction is
> correctly fail-closed, but the funded window is unlaunchable under the audited bytes; the
> recorded standing constraint ('NO REBOOT before T-0 or the evidence re-authors') is
> insufficient — no reboot happened and the capability still died of monotonic age from the
> window slip. Remedy (re-author evidence, reissue freeze receipt, re-pin plan tree, recommit)
> changes pack bytes, rotates the committed pack digests, and voids the audit-baseline
> manifest's pack digests under charter amendment 12 — the council must schedule this re-freeze
> before or at GO.

**Seat-report citation:** L1 report **line 76** (B1 paragraph) and **line 62** (probe 6, the
executed census: "all 33 freeze evidence receipts across the three packs are past
`valid_until_monotonic_ns`").
**Refuter corroboration:** `cold-fable-ruling.md:19` — "B1 (33/33 evidence receipts expired —
executed by A-execution refuter)".
**Verdict interaction:** not struck; drives Phase 0 ruling **R1** and Phase 2
(`council-verdict.md:74-76`, `97-100`). Opus **W2** (`opus-contract-refuter-findings.md:59`):
"The re-freeze remedy rotates pack digests and therefore voids this audit's own baseline
manifest."

### F2 — [blocker] (seat label **B2**)
**Title (verbatim):** Authoritative work-selection state fails open for quiet-window selection:
no council gate, and a superseded campaign renders READY [QUIET-MAC]

**`file_line` (verbatim):** `docs/process/state_kernel.json (active_global_gates: []);
RUN_STATE.md:3433`

**failure_scenario (verbatim):**
> A successor session or tired operator obeys RUN_STATE's generated region, which today renders
> 'READY — Q2 P2-006: Window A two-model campaign' with zero active global gates — despite Ed's
> 2026-08-13 window-gating directive (windows sit behind the council verdict) and despite D-117
> having superseded the Window-A program. A quiet night gets spent on a campaign whose outputs do
> not trace to the current claim path, bypassing the council gate entirely, because the gate
> exists only in decision-log prose while the kernel's purpose-built gate machinery (proven
> working by probe) carries no gate row. The actual funded program (three frozen D-117 packs) has
> no kernel row at all.

**Seat-report citation:** L1 report **line 78** (B2) and **line 63** (probe 7, gate positive
control).
**Refuter corroboration:** `cold-fable-ruling.md:19` — "B2 (kernel fail-open — re-confirmed
`active_global_gates: []` and the P2-006 READY [QUIET-MAC] row on primary bytes; confirmed by
both DG lenses)"; `opus-contract-refuter-findings.md:21` — "sweep-B5: state kernel stale / no
active gates — independent corroboration of fleet blocker L1-B2".
**Verdict interaction:** B2's own citation of `RUN_STATE.md:3433` is what **struck** the
magistrate's drift rationale — `council-verdict.md:30-32`: "The original rationale's 'RUN_STATE
in no lens's universe' claim is stricken (L1-B2 itself cites RUN_STATE.md:3433)."

### F3 — [blocker → RE-SEVERITIED to should_fix] (seat label **B3**)
**Title (verbatim):** Work-selection authority is bifurcated: launch-blocking work orders live as
hand-written prose outside the generated region while kernel rows assert falsehoods

**`file_line` (verbatim):** `TASK_QUEUE.md:201,635,659 (outside markers 452-613);
docs/process/state_kernel.json /tasks/D117-U11-IDPIN-PROJECTION`

**failure_scenario (verbatim):**
> WO-MINT-ESTIMATOR-VOCAB, WO-COLLECTION-MARGIN-01, and WO-ARM-EVIDENCE-AUTHOR-01
> ('LAUNCH-BLOCKING for any window night') were 'registered in TASK_QUEUE' as hand-written
> sections outside the marker-fenced generated region — invisible to gen_state --check and absent
> from the kernel, violating DOC-008's single-authority contract. Simultaneously the kernel's
> D117-U11-IDPIN-PROJECTION row still reads 'queued... Checked-in packs remain unprojected' at a
> head whose packs carry PASS projection and freeze receipts, and FLOOR-COMMONMODE-01 renders
> 'READY [AGENT]' despite its D-133 desk-thread disposition. A session trusting the declared
> AUTHORITATIVE_WORK_SELECTION_STATE misses launch-blocking obligations or resumes disposed work;
> a session trusting the prose contradicts the kernel.

**Seat-report citation:** L1 report **line 80** (B3).
**RE-SEVERITIED BY THE VERDICT — `council-verdict.md:41-43`, Disposition 3 (verbatim):**
> 3. **L1-B3 severity — should_fix**, remedy subsumed into the blocker-gated
>    kernel-reconciliation transaction (cold §D; discharges Opus S10). P2-006 is retired only by
>    formal ruling, never silent deletion.

Supporting: `cold-fable-ruling.md:61` — "## D. SEVERITY SYNTHESIS — L1-B3 authority
bifurcation: SHOULD-FIX, remedy launch-gated via L1-B2"; `opus-contract-refuter-findings.md:47`
— "**S10 — L1-B3's severity synthesis should be ruled at the pairing, not in-loop.**
(Discharged: the cold adjudicator ruled it.)"

### F4 — [should_fix] (seat label **S1**)
**Title (verbatim):** D-118's 'mechanical enforcement' of the merge gate ledger does not exist
anywhere in the repo

**`file_line` (verbatim):** `docs/decision_log.md:7753-7759; .github/workflows/ (no checker)`

**failure_scenario (verbatim):**
> D-118 states 'every PR description must carry a GATE LEDGER... any item marked NOT-RUN blocks
> the merge' and frames this as mechanical, but grep finds no gate-ledger checker in CI or
> scripts — enforcement is agent discipline, the exact prose-only failure mode D-118's own
> trigger recorded. A PR merges on green CI with an incomplete ledger and nothing mechanical
> objects. (Contrast: D-121's terminal review IS machine-bound for windows via exact commit
> trailers — arm_readiness_evidence_t0.py:913-943.)

**Seat-report citation:** L1 report **line 82** (S1); D-121 enforcement contrast at line 70.
**Verdict interaction:** none — L1-S1 is **not named** in the verdict's Phase-1 should-fix batch
(`council-verdict.md:85-87`, which enumerates *sweep* B1/B2/B3/B6/B7 + D-130 + L11's three paper
corrections).

### F5 — [should_fix] (seat label **S2**)
**Title (verbatim):** kernel.updated and latest_report are false, and no invariant forces them to
move

**`file_line` (verbatim):** `docs/process/state_kernel.json (updated: 2026-08-08; latest_report
label: T3 2026-08-09)`

**failure_scenario (verbatim):**
> The kernel says updated 2026-08-08 while its own row notes cite 2026-08-11/12 events, and
> latest_report describes the T3 2026-08-09 session six sessions ago; the validator checks only
> date format, so the render carries a false freshness signal that consumers use to weigh trust
> in the generated views.

**Seat-report citation:** L1 report **line 84** (S2).

### F6 — [should_fix] (seat label **S3**)
**Title (verbatim):** FREEZE-FCM01.md's standing prohibition was never amended after D-133 cl.4
executed the re-spec

**`file_line` (verbatim):** `FREEZE-FCM01.md:1-8 (banner: 'Do not fix, do not consume, do not
register in any pack')`

**failure_scenario (verbatim):**
> The root-level FROZEN banner still bars pack registration of the estimator and says only Ed may
> relicense, while the frozen packs lawfully register d124_two_shared_edge_common_mode.v1 under
> Ed's later cl.4 EXECUTE ratification. A successor session reading the banner as binding either
> stalls the lane or concludes the packs violate a standing freeze order; the repo's own
> convention (dated supersession notes on consult docs) was not applied here.

**Seat-report citation:** L1 report **line 86** (S3).

### F7 — [nit] (seat label **N1**)
**Title (verbatim):** Frozen pack bytes still carry draft_status 'unfrozen_draft' — the M-2 scoped
override remains the operative instrument indefinitely

**`file_line` (verbatim):** `configs/campaigns/d117_floor_qwen25_1p5b_v1/plan_tree.json:793`

**failure_scenario (verbatim):**
> No code consumes draft_status (verified by grep), so this is cosmetic, but because the bytes are
> now frozen the M-2 'until the generator fix lands' override can never be retired for these packs
> without a reissue; the §5C human gate must permanently rely on the recorded override.

**Seat-report citation:** L1 report **line 88** (N1). Cold ruling `cold-fable-ruling.md:55`
independently verified the same bytes at HEAD and ruled the M-2 remedy **incomplete as recorded**.

### F8 — [nit] (seat label **N2**)
**Title (verbatim):** gen_state invariant 8's D-041 authority binding is a label-substring match

**`file_line` (verbatim):** `scripts/gen_state.py:372`

**failure_scenario (verbatim):**
> The post-2M authority check passes if the string 'D-041' merely appears in the authority label; a
> mislabeled pointer to any document mentioning D-041 satisfies it. Low stakes — it is a lint over
> hand-written labels, not a gate.

**Seat-report citation:** L1 report **line 90** (N2).

### Findings STRUCK by the verdict that touch L1
None of L1's eight findings were struck. `council-verdict.md:44-45` (Disposition 4) strikes
L8-B4, WO-L2-4, and F4's timing premise — none is an L1 finding (note the name collision: that
"F4" is L4/T-0 lane, not L1's F4/S1). The only L1 alteration is the **B3 severity remand to
should_fix** (Disposition 3, lines 41–43).

### L1 work orders, verbatim (`raw/L1-triage.md:44-54`)
- **WO-L1-1 (blocker B1):** ruled disposition for the expired pack freeze evidence — re-author
  evidence + reissue freeze receipts + re-pin plan trees + recommit on the production machine, or
  amend the evidence-validity design by decision (freeze-side evidence bound to boot session only,
  monotonic expiry reserved for arm-side); then re-pin the audit-baseline manifest per charter
  amendment 12 and re-discharge the §5C committed-pack verification
- **WO-L1-2 (blocker B2):** add WINDOW-COUNCIL-GATE to state_kernel.json active_global_gates
  (scope quiet_mac, allowed_task_ids [], authority = 2026-08-13 window-gating directive,
  clearance = council READY + T-0 GO); regenerate views; remove only on the council verdict
- **WO-L1-3 (blocker B3):** kernel truth pass — bump updated, correct latest_report, reconcile
  D117-U11-IDPIN-PROJECTION and FLOOR-COMMONMODE-01 to landed/disposed reality, enroll
  WO-ARM-EVIDENCE-AUTHOR-01 / WO-COLLECTION-MARGIN-01 / WO-MINT-ESTIMATOR-VOCAB as kernel rows
  with satisfied evidence where landed, and demote the hand-written TASK_QUEUE sections to
  pointers at their kernel rows
- **WO-L1-4 (should-fix S1):** build the D-118 PR gate-ledger mechanical lint in CI, or amend
  D-118 to state enforcement is procedural
- **WO-L1-5 (should-fix S3):** add a dated supersession banner to FREEZE-FCM01.md citing the D-133
  cl.4 execution ratification

> **Tracking fact (assembler-verified):** the identifiers `WO-L1-1` … `WO-L1-5` appear **nowhere**
> in the repository outside `docs/process_traces/2026-08-15-readiness-council/`
> (`grep -rn "WO-L1-" docs/` → only `triage.json` and the two seat reports). L1's work orders were
> never enrolled as TASK_QUEUE rows or kernel rows under their own IDs; the repairs below are
> mapped by content, not by ID.

---

## 2. WHAT CHANGED SINCE 2026-08-15

### F1 / B1 — expired freeze evidence, D-137, and the freeze-0002 → freeze-0003 re-mint chain

**(a) The ruling (Phase 0 R1) — LANDED.** `docs/decision_log.md:9196` — "### R1 RULED
(magistrate synthesis of the rule-11 cold gate, 2026-08-15): freeze-evidence lifecycle —
content-bound design ADOPTED WITH THE COMPOSED AMENDMENT SET". Gate custody:
`docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/` (4 files: `consult.md`,
`consult-prompt.md`, `coldgate-adjudicator-ruling.md`, `coldgate-opus-refuter-findings.md`).
Operative clauses quoted verbatim from the decision log:
- cl.1 (`:9206-9215`): taxonomy SPLIT — `RE_DERIVABLE` (DOCTRINE_PIN, PACK_FAMILY — "no stored
  validity at all") / `EXECUTION_BOUND` ("RETAIN boot binding + horizon until Ed's
  execution-environment-fingerprint ruling lands") / TIME_BOUND / SESSION_STATE_BOUND /
  TEMPORAL_CAPABILITY.
- cl.5 (`:9237-9239`): "**NO GRANDFATHERING** (both seats + contract text): the 33 expired v1
  receipts are never revalidated; migration is fresh re-authoring within the Phase-2 successor
  family, one atomic family transaction."
- cl.6 (`:9240-9247`): Ed's reserved list (horizons, environment-fingerprint comparison semantics,
  refusal-code spellings, successor pack IDs + cross-chain numbering, freeze-receipt v2 predecessor
  bindings + family publication marker, and "the irreversible successor-family publication and
  Phase-3 baseline identity — rule-11 irreversible triggers, Ed approval mandatory").
- **Implementation amendments:** `:9252` ("R1 implementation amendment — 2026-08-17 (Phase-2
  preparation only; no publication)") and `:9320` ("R1 implementation amendment — FIX ROUND 1
  lifecycle enforcement (2026-08-17)"). `:9264-9268` defines the split exact-key schemas:
  `joulewise.arm_readiness_content_evidence_receipt.v1` ("carries neither `boot_session_id` nor
  `valid_until_monotonic_ns`") and `joulewise.arm_readiness_execution_evidence_receipt.v1`
  ("retaining both fields").
- **D-137 amended, zero reach over content receipts:** `:9290-9295`.

**(b) The re-mint transaction (Phase 2, executed as D-146/D-147) — LANDED ON THE BRANCH, NOT ON
MAIN.** Decision-log index rows: `docs/decision_log.md:169` (D-146, R1 production capture-pipeline
v3) and `:170` (D-147, R2 mint-lane fan-out composite — "immutable `_v3` pack family bound at
birth to the LIVE generation… `_v2` packs READ-ONLY including their generators… **freeze-0003
chained to freeze-0002 (parked step 6 AMENDED — no freeze-0002 re-mints)**"). Ruling homes:
`docs/process_traces/2026-08-19-r1-r2-codesign/13-r1-ruling.md`, `14-r2-ruling.md`,
`15-amendment-r6.md`.

Commit chain verified present and ancestral to HEAD:

| Commit | Subject (verbatim from `git log`) |
|---|---|
| `1d3873b` | S3: d117 _v3 pack family emitted via unedited _v2 generators, bound to r6 at birth; family tests (successor emission, replay integrity, byte preservation) |
| `3d05982` | D-147 S5/U11: identity-pin projection frozen for d117_floor_qwen25_1p5b_v3 (projection-0001, 2 units, PASS) |
| `6fd8bce` | D-147 S5/U11: identity-pin projection frozen for d117_floor_qwen25_7b_v3 (projection-0001, PASS) |
| `74632e3` | D-147 S5/U11: identity-pin projection frozen for d117_contrast_qwen25_1p5b_vs_7b_v3 (projection-0001, PASS) |
| `5e38f1e` | D-147 S5: freeze-0003 minted for d117_floor_qwen25_1p5b_v3 (PASS; predecessor _v2/freeze-0002 1277103b…; receipt 0abfddb1…) |
| `eb7f6c6` | D-147 S5: freeze-0003 minted for d117_floor_qwen25_7b_v3 (PASS; predecessor _v2/freeze-0002 decd8cdc…) |
| `94dc3b3` | D-147 S5: freeze-0003 minted for d117_contrast_qwen25_1p5b_vs_7b_v3 (PASS; predecessor _v2/freeze-0002 18855647…) |
| `8b2b021` | S5 COMPLETE: confirmation table filled (three freeze-0003 receipts + committed tree digests) |
| `75cb868` | S6 bookkeeping: kernel transaction (window rows -> _v3, REFREEZE-D147-CLOSE row, latest_report; regen + test pins), T12/T13 run report, README blurb refresh |

**Assembler-executed verification at `b92b43d` (read-only):**
- `configs/campaigns/{d117_floor_qwen25_1p5b_v3, d117_floor_qwen25_7b_v3,
  d117_contrast_qwen25_1p5b_vs_7b_v3}/arm_readiness.freeze.receipts/freeze-0003.json` all exist
  with `"status": "PASS"`, 14 rows, `"refusals": []`, `receipt_kind` present, and a `predecessor`
  block naming `arm_readiness.freeze.receipts/freeze-0002.json` in the corresponding `_v2` pack
  plus `"pack_digest_algorithm": "joulewise.committed_pack_tree_sha256.v1"`.
- Recomputed `joulewise.arm_readiness.committed_pack_tree_sha256` over the three `_v3` packs:
  **all three MATCH** the S5 confirmation table's committed tree digests
  (`1e3f1fa3…`, `6d0b9b75…`, `0d071941…`).
- **33 evidence receipts (11 per `_v3` pack) re-authored**, all `schema_version:
  "joulewise.arm_readiness_evidence_receipt.v1"` — i.e. the **legacy generic v1 schema**, each
  carrying BOTH `boot_session_id` and `valid_until_monotonic_ns`, not the R1 split schemas of
  decision-log `:9264-9268`.
- `boot_session_id` on every `_v3` evidence receipt: `da90818c-9c31-45d0-8813-deae65fba143`;
  live `sysctl kern.bootsessionuuid` at probe time: `DA90818C-9C31-45D0-8813-DEAE65FBA143` —
  **same boot session, no reboot**.
- **Validity horizon (the B1 mechanism), measured at probe time:** min
  `valid_until_monotonic_ns` per pack = `2468742407178458` (1p5b_v3), `2468774933440083` (7b_v3),
  `2468792444508708` (contrast_v3); live `CLOCK_UPTIME_RAW` = **`2414989316822250`** →
  **≈ 53,753 s ≈ 14.9 h of headroom remaining** on the earliest-expiring receipt.
- `joulewise/arm_readiness_evidence.py:42` — `_EVIDENCE_VALIDITY_NS = 86_400 * 1_000_000_000`
  (unchanged 24-hour blanket horizon); `:2421` — `valid_until = evaluated_at_monotonic_ns +
  _EVIDENCE_VALIDITY_NS`.
- RUN_STATE.md:210-212 states the same clock in prose: "The S4 evidence **EXPIRES
  ~2026-08-20T16:51Z** and **DIES ON ANY REBOOT** (boot session da90818c…). **NO REBOOTS** until
  the mints land or Ed chooses re-authoring."
- No successor row registry exists: `configs/arm_readiness/` contains only
  `d117_row_registry_v1.json`; the R1 lifecycle registry with the five Ed-reserved values is
  **not installed** (`grep -rn ED_RESERVED configs/` → no hits; the `ED_RESERVED` sentinels live
  only in `joulewise/arm_readiness.py` + two test modules). Decision-log `:9300-9303`: "Exact
  spellings and type labels remain Ed-reserved under R1 clause 6… The checked-in placeholder uses
  explicit `ED_RESERVED:` values and refuses issuance/consumption". D-148.5
  (`docs/decision_log.md:171`) defers those five values to council; RUN_STATE.md:94-96 lists the
  registry council as item 2 of the five-day sequence — **not yet run**.

**(c) Delivered-evidence text where the queue states it.** TASK_QUEUE.md carries no row for
WO-L1-1. The nearest queue statements are the three gated window rows, e.g. **TASK_QUEUE.md:527**
(Q2 D117-W-ALPHA): "Exact frozen pack **d117_floor_qwen25_1p5b_v3** is used only after council
READY and separate T-0 GO… **The pack is frozen but not selectable**: WINDOW-COUNCIL-GATE admits
no quiet-mac task, and council Phase 2 requires the ruled successor re-freeze before the re-audit
and READY-candidate sitting."

### F2 / B2 — WINDOW-COUNCIL-GATE kernel installation

**LANDED.** TASK_QUEUE.md:104 (Completed row, verbatim delivered-evidence cell):
> | WO-KERNEL-RECONCILE | P1 Phase Gate | 2026-08-15 | Install the council work-selection gate in
> the state kernel and retire P2-006 per R3 | No phase exit-checklist matrix row exists. Merged
> via #150 (`47d2645`): the WINDOW-COUNCIL-GATE is live (no quiet-mac selection before a
> READY-candidate council verdict), P2-006 formally retired by supersession, kernel truth pass in
> one transaction; magistrate-supervised meta-process edit. |

Commit resolved: `47d2645 2026-08-15 WO-KERNEL-RECONCILE: council gate installed, P2-006 retired
(R3), kernel truth pass (one transaction) (#150)` — ancestor of HEAD.

**Assembler-verified kernel state at `b92b43d`** (`docs/process/state_kernel.json`):
```
active_global_gates: [ {
  "id": "WINDOW-COUNCIL-GATE",
  "allowed_task_ids": [],
  "scope": {"lanes": ["quiet_mac"], "operation": "select"},
  "authority": ["docs/decision_log.md#window-gating-directive--2026-08-13-late-ed-t6-council-audited-instrument-readiness-precedes-any-window",
                "docs/process_traces/2026-08-15-readiness-council/council-verdict.md#verdict"],
  "clearance": "docs/process/instrument-readiness-audit-charter.md#verdict-form-amendments-11-12 — a reconvened READY-CANDIDATE council verdict records no NOT-READY, no UNVERIFIED, and all ED-QUALIFICATION rows closed with evidence",
  "summary": "No quiet-mac task may start or resume after the 2026-08-15 NOT-READY verdict; the frozen D-117 packs wait while the council repair program proceeds." } ]
```
Every element of WO-L1-2's contract is present, and the clearance string is stricter than the
work order's ("council READY + T-0 GO"): it binds the charter's amendment-11/12 form **including
ED-QUALIFICATION rows closed with evidence**.

**Rendered effect (generated region):** TASK_QUEUE.md:527/616 Q2 D117-W-ALPHA, :528/617 Q3
D117-W-BETA, :529/618 Q4 D117-W-GAMMA, :530/619 Q5 P2-010, :534/623 Q10 P2-046B all render
`GATED — WINDOW-COUNCIL-GATE` or `BLOCKED — …`. The gate section header is at TASK_QUEUE.md:591.
P2-006 no longer appears as a task id in the kernel (three residual occurrences, all
`"target": "P2-006-SUCCESSOR-ROW"` at `state_kernel.json:1933, 2037, 2090`) — consistent with
Disposition 3's "P2-006 is retired only by formal ruling, never silent deletion" and the R3
ruling cited in the queue row.

### F3 / B3 — kernel truth pass and authority bifurcation

**PARTLY LANDED in the same `47d2645` transaction; assembler-verified at `b92b43d`:**

| WO-L1-3 element | State at HEAD |
|---|---|
| bump `updated` | **DONE** — `updated: 2026-08-19` |
| correct `latest_report` | **DONE** — label "T12/T13 session 2026-08-19: co-design first application (R1/R2 rulings), D-147 transaction executed S0-S5 …", path `docs/run_reports/2026-08-19-t12-t13-session.md` |
| reconcile `D117-U11-IDPIN-PROJECTION` | **row absent** — `grep -c D117-U11-IDPIN-PROJECTION state_kernel.json` = **0** |
| reconcile `FLOOR-COMMONMODE-01` | **row absent** — `grep -c FLOOR-COMMONMODE-01 state_kernel.json` = **0** |
| enroll WO-ARM-EVIDENCE-AUTHOR-01 / WO-COLLECTION-MARGIN-01 / WO-MINT-ESTIMATOR-VOCAB as kernel rows | **NOT DONE as kernel rows** — none of the three is a key in `/tasks` (73 tasks total). All three instead appear as Completed TASK_QUEUE rows: :107 (`ac3fe1d`, #149), :108 (`1092984`, #143), :109 (`e11b1ad`, #140) |
| demote the hand-written TASK_QUEUE sections to pointers | **NOT DONE** — full hand-written sections persist OUTSIDE the generated region (markers now at TASK_QUEUE.md:511 BEGIN / :693 END): `## WO-MINT-ESTIMATOR-VOCAB — COMPLETED` at **:207**, `## WO-COLLECTION-MARGIN-01 — COMPLETED` at **:733**, `## WO-ARM-EVIDENCE-AUTHOR-01 — COMPLETED` at **:761**. Their "LAUNCH-BLOCKING" framing is gone (all three read COMPLETED with merge SHAs) |
| — (new, post-verdict) | **Additional hand-written WO sections outside the markers with NO kernel row:** `## WO-SAMPLER-SUPERVISOR` (:293), `## WO-CRASHMATRIX-RELIABILITY` (:336), `## WO-DETERMINISM-LOAD-ISOLATION (registered 2026-08-19, T12…)` (:363), `## WO-LAUNCH-BINDING stage checkpoint` (:491). Kernel rows DO exist for `WO-DETECT-PULSES-BUDGET`, `WO-LAUNCH-BINDING`, `WO-PROOF-RUNNABILITY-REPAIR` |
| new transaction row | **PRESENT** — `/tasks/REFREEZE-D147-CLOSE`, status `active`, lane `agent`, note: "S0-S5 executed 2026-08-19; freeze-0003 x3 minted and landed (8b2b021); r6 live; canonical at the frozen head in flight" |

### F4 / S1 — D-118 gate-ledger mechanical lint

**NOTHING CHANGED.** `grep -rniE "gate.?ledger" .github scripts` at `b92b43d` returns **zero
hits**. `.github/workflows/` contains exactly `ci.yml`, `d117-production-proof.yml`, `site.yml`.
D-118's index row (`docs/decision_log.md:143`) still reads "…and **MECHANICALLY CHECKED** via a
per-PR gate ledger; D-072 self-merge is conditioned on that ledger being complete" — i.e. neither
limb of WO-L1-4 (build the lint **or** amend D-118 to say "procedural") was executed. The verdict
never scheduled it: L1-S1 is absent from `council-verdict.md:85-87`'s should-fix batch.

### F5 / S2 — kernel freshness

**CURED** (see the F3 table): `updated: 2026-08-19`; `latest_report` points at the T12/T13
session. **No automated staleness detector was located** — the seat's own unexecuted obligation
("No automated staleness detector for kernel.updated was built; the truth check was manual",
`raw/L1-triage.md:72`) remains unaddressed; `grep` finds no such invariant added to
`scripts/gen_state.py`.

### F6 / S3 — FREEZE-FCM01.md supersession banner

**NOTHING CHANGED.** At `b92b43d`, `FREEZE-FCM01.md:1-7` still reads:
> # FLOOR-COMMONMODE-01 — FROZEN (2026-08-11, terminal cold-gate condition executed)
> **State:** FROZEN at db3e212 (+ the round-4 delta audit). The cold gate's licensing authority on
> this unit is SPENT (final synthesis, 2026-08-10/11). **Only Ed may relicense further work. Do
> not fix, do not consume, do not register in any pack.**

`grep -n "D-133\|supersed\|SUPERSED\|2026-08-1" FREEZE-FCM01.md` returns lines 1, 4 and 53 only;
line 53's "superseded by this freeze banner" is the banner superseding *other* text, not a dated
D-133 cl.4 supersession note. WO-L1-5 is unexecuted.

### F7 / N1 — `draft_status` in frozen bytes

**Persists in `_v1` exactly as predicted; cured by construction in the successor family.**
`configs/campaigns/d117_floor_qwen25_1p5b_v1/plan_tree.json:793` still reads `"draft_status":
"unfrozen_draft"`. The `_v2` and `_v3` plan trees contain **no `draft_status` key at all**
(grep returns nothing). The nit's own prediction — "can never be retired for these packs without
a reissue" — is now literally the state of the record: the reissue happened as a **new family**
(`_v3`), and `_v1` keeps the byte forever.

### F8 / N2 — `gen_state.py` D-041 substring lint

**NOTHING CHANGED.** `scripts/gen_state.py:372` (assembler-read, lines 368–373):
```
if tid in ("P2-022", "P2-023") and "D-041" not in task["authority"]["label"]:
    fail(f"{where}: post-2M authority must resolve to D-041")
```
Still a substring match. (Adjacent observation for the seat: invariant 8's other limb at :371
still requires a `"target": "P2-006"` task dependency, while P2-006 has been retired and the
kernel now carries only `P2-006-SUCCESSOR-ROW` targets.)

### The audit-baseline manifest — re-pin / SUPERSESSION question (charter amendment 12)

**NOT SUPERSEDED. The manifest is unchanged since it was cut, and its pack digests no longer
reproduce at the current head.**

- Verdict language, `council-verdict.md:30-32` (Disposition 1): "…every manifest binding
  recomputes byte-identical at that head, including all three pack digests via
  `joulewise.arm_readiness.committed_pack_tree_sha256`. … **Future manifest changes are worded as
  SUPERSESSION, never re-pin** (charter calls the manifest immutable)."
- Verdict language, `council-verdict.md:68-70` ("Manifest conditions at supersession", cold §B.2 /
  Opus S11): "add `pack_digest_algorithm`, the chain-template coverage note (embedded in runbook
  §6, covered by runbook_sha256), and **paths for all bindings**. The magistrate's earlier
  'manifest requires NO fix' is rejected."
- Verdict language, `council-verdict.md:102-104` (Phase 3): "baseline-manifest **SUPERSESSION**
  (with the ruled fields) + focused re-audit of pack/custody-bearing seats (**L1, L5, L7
  minimum**) + adversarial coverage re-enumeration of all universes".
- **File history:** `git log --oneline -- docs/process/audit-baseline-manifest.json` returns
  **exactly one commit** — `694442c Audit-baseline manifest committed at the readiness-tooling
  head (charter amendment 2): the eleven-seat fleet's immutable reference`. No superseding
  manifest file exists anywhere under `docs/` (`find docs -iname "*baseline*manifest*"` → the
  single file).
- **Ruled fields still absent:** the manifest at HEAD has keys `acceptance_artifact_sha256`,
  `arm_packet`, `charter`, `freeze_manifest_sha256`, `governing_decisions`, `head_commit`,
  `invalidation_rule`, `origin_main`, `pack_digests`, `row_registry_sha256`, `runbook_sha256`,
  `schema`, `state_kernel_sha256`. There is **no `pack_digest_algorithm` key** and **no per-binding
  path fields** (only bare sha256 scalars). It still pins `head_commit` / `origin_main` =
  `ac3fe1d…` and the three **`_v1`** pack digests.
- **Executed refutation of the manifest's own bindings at `b92b43d`** (assembler ran
  `joulewise.arm_readiness.committed_pack_tree_sha256` over each `_v1` pack and compared to
  `pack_digests`): **all three MISMATCH.**

  | pack | manifest `pack_digests` | recomputed at `b92b43d` |
  |---|---|---|
  | `d117_floor_qwen25_1p5b_v1` | `f4c02c8a697c3a0d…` | `5def6e514116184d106702a5…` |
  | `d117_floor_qwen25_7b_v1` | `6a8a3bf6527855bb7c…` | `2091df582c9fa5aa7b513d53…` |
  | `d117_contrast_qwen25_1p5b_vs_7b_v1` | `1cc0c784ec573981…` | `878f16eadfbfe70415ecab5d…` |

  Cause, isolated by `git diff --stat ac3fe1d..HEAD -- configs/campaigns/<pack>`: in each `_v1`
  pack **exactly one file changed — `generate_configs.py`** (+576/−72, +580/−76, +578/−67
  respectively; the successor-generator repair stream of 2026-08-17/18). Working tree is clean
  (`git status --porcelain` empty). The manifest's own `invalidation_rule` reads: "any repo change
  after this manifest voids affected lens results (charter, amendment 12)".
  This is Opus **W2** arriving on schedule (`opus-contract-refuter-findings.md:59`: "Absent that
  ordering the next sitting will discover its baseline is already dead").

---

## 3. ED-QUALIFICATION ROWS

Charter rule in force for this sitting: `council-verdict.md:54-57` — "READY-CANDIDATE sittings
(charter 77-78 binds: **only T0 rows may remain open**)". Both L1 rows are declared **stable
capability** in their own text, so neither qualifies for the T0 exemption.

> **Tracking fact:** `ED-QUAL-L1-1` and `ED-QUAL-L1-2` appear **nowhere in the repository outside
> `docs/process_traces/2026-08-15-readiness-council/`**. Searched: `grep -rn
> "ED-QUAL-L1-1\|ED-QUAL-L1-2" --include=*.md --include=*.json .` over the whole tree (hits only
> in `triage.json`, `sitting-packet-FINAL.md`, `cold-fable-ruling.md:99`, the L1 seat report);
> `RUN_STATE.md`; `TASK_QUEUE.md`; `docs/process/state_kernel.json`;
> `docs/phase_2/ed-qualification-session.md`; `docs/process/ed-batch-packet.md`;
> `docs/process/ed-evening-checklist.md`; `docs/process/ed-morning-packet-2026-08-18.md`;
> `docs/run_reports/2026-08-18-t10-session.md`. Only `ED-Q-L9-3` is tracked by ID in live surfaces.
> **There is no ED-row closure ledger.** Closure below is reconstructed from primary artifacts.

### ED-QUAL-L1-1
**Row text VERBATIM (`raw/L1-triage.md:58`):**
> ED-QUAL-L1-1 (stable capability, before the sitting): same-boot production replay of the freeze
> chain — run scripts/generate_arm_readiness.py verify against each pack's freeze receipt and
> scripts/project_identity_pins.py verify with the real model bytes on the production Mac (boot
> session da90818c-9c31-45d0-8813-deae65fba143). The sandbox cannot discharge this: model bytes
> are absent, so U11 refuses readiness_identity_artifact_unreadable (observed, fail-closed).

**Kind:** declares itself **stable capability** (not T0/perishable) — and additionally "before the
sitting".

**LOCATED CLOSURE EVIDENCE — PARTIAL, and for a different pack family and a different subcommand:**
- Production machine work on the same boot session DID occur: the S5 mints ran at
  `/Users/edr/JouleWise-measurement-20260818` (verified: that checkout exists, is on
  `impl/r2-s0-mint-resolver`, head `94dc3b34` = the third freeze-0003 commit). Procedure and
  authority: `docs/process/ed-s5-mint-decision-2026-08-19.md:55-64` (the exact six commands) and
  `docs/decision_log.md:171` (D-148.1).
- The six executed commands were `project_identity_pins.py **freeze**` ×3 and
  `generate_arm_readiness.py **freeze**` ×3 — **not** the `verify` subcommand this row names.
- Real model bytes WERE exercised: the `_v3` U11 projection receipts are `status: PASS` with
  populated `checks[].observed` model/config/runtime shas (e.g. `model_artifact_sha256:
  fea4cb94…`), which the sandbox provably cannot produce.
- Lead-side verification of the receipts is asserted (not independently audited) in
  `RUN_STATE.md:169-171` and `docs/process/ed-s5-mint-decision-2026-08-19.md:66-69`: "Claude
  performs it plus the full receipt verification (path-binding, PASS, `freeze-0003`, predecessor
  triple vs the `_v2` receipts, digests for the confirmation table)."
- **NO evidence located of `generate_arm_readiness.py verify` or `project_identity_pins.py verify`
  being run against the `_v1` freeze receipts on the production Mac.** Searched:
  `docs/process_traces/2026-08-19-refreeze-execution/{s4,reports,suite-logs}/` file listings (the
  s4 logs are `author-*`, `check-*`, `suite-tests.*` — no `verify-*`); the T10 qualification table
  (`docs/run_reports/2026-08-18-t10-session.md:102-110`), which lists D-127 sudoers, sampler
  lifecycle, rail probe, backlight, ED-QUAL-L4-1 decisive replay, ED-Q-L9-3 census, and dress
  rehearsal **OPEN** — and no freeze-chain replay row; `~/JouleWise-window-custody/` top-level
  listing.
- **Countervailing ruling the seat must weigh:** R1 cl.5 (`docs/decision_log.md:9237-9239`) —
  "**NO GRANDFATHERING** … the 33 expired v1 receipts are **never revalidated**". A same-boot
  replay of the `_v1` freeze chain may now be a *prohibited* act rather than an owed one; if so
  the row needs re-scoping to the `_v3` family rather than closing on `_v1` evidence.

### ED-QUAL-L1-2
**Row text VERBATIM (`raw/L1-triage.md:60`):**
> ED-QUAL-L1-2 (stable capability, after the B1 disposition is ruled): re-author the pack-side
> freeze evidence (scripts/author_arm_readiness_evidence.py), reissue freeze receipts, update
> plan-tree pins, and recommit on the production machine — must run there because evidence
> receipts derive kern.bootsessionuuid and monotonic time from the arming host; any reboot
> decision is Ed's.

**Kind:** declares itself **stable capability**, conditioned on the B1 disposition being ruled
(it was — R1, `docs/decision_log.md:9196`).

**LOCATED CLOSURE EVIDENCE — SUBSTANTIALLY EXECUTED, on the `_v3` successor family:**
- **Re-author on the production machine:** `RUN_STATE.md:221-223` — "S4 evidence **33/33 PASS
  authored at the measurement checkout** (its git state: branch checked out, S4 commit landed to
  origin via pull)". Custody:
  `docs/process_traces/2026-08-19-refreeze-execution/s4/` (`author-1p5b_v3.json`,
  `author-d117_floor_qwen25_7b_v3.json`, `author-d117_contrast_qwen25_1p5b_vs_7b_v3.json`,
  `authored-files.sha256`, per-pack `check-*.log`, and eleven `suite-tests.*.log`).
- **Reissue freeze receipts:** commits `5e38f1e`, `eb7f6c6`, `94dc3b3` (all PASS, predecessor
  triple recorded).
- **Plan-tree pins / recommit:** the `_v3` packs are committed and their committed tree digests
  recomputed MATCH the confirmation table (assembler-verified, §2 above).
- **Confirmation table filled** (`8b2b021`):
  `docs/process/ed-s5-mint-decision-2026-08-19.md:71-85` — header verbatim: "## Confirmation table
  (COMPLETE — S5 executed 2026-08-19 under D-148.1, mints via Ed-approved manual prompts)", with
  the three freeze-0003 shas + committed tree digests.
- **What is NOT closed inside this row:** (i) Ed's **exact-byte publication confirmation** is
  explicitly still owed — `docs/process/ed-s5-mint-decision-2026-08-19.md:94-95` ("final
  exact-byte publication confirmation (this table, post-mint)") and `RUN_STATE.md:82-84` (Ed's
  retained items include "exact-byte confirmation"); (ii) the re-authored evidence is the **legacy
  v1 generic schema with the same 24 h horizon**, not the R1 split schemas, so the row's underlying
  defect class is reset rather than retired (see §5 probe 3); (iii) nothing is merged to main.

---

## 4. CANDIDATE DISPOSITIONS FOR THE SEAT TO ADJUDICATE

Candidate dispositions are assembled, not adjudicated; the seat rules.

| Item | Candidate disposition |
|---|---|
| **F1 / B1** — 33 freeze receipts monotonically expired | **STILL-OPEN (transformed).** Repair evidence attached and mechanically verified (`_v3` family, freeze-0003 ×3 PASS, digests reproduce). Remaining: (a) the re-minted evidence uses the **same 24 h monotonic horizon** and the same `joulewise.arm_readiness_evidence_receipt.v1` schema, with **≈14.9 h headroom measured at probe time** and a stated death at ~2026-08-20T16:51Z or any reboot; (b) the R1-ruled split schemas / content-bound lifecycle are **not in force** for these packs (registry uninstalled, five values still at council per D-148.5); (c) nothing merged to main; (d) `_v1` receipts remain expired and are ruled never-revalidated |
| **F2 / B2** — kernel fails open, no council gate | **READY-evidence-attached.** `WINDOW-COUNCIL-GATE` live in `active_global_gates` with the exact contracted shape and a **stricter** clearance (charter amendments 11–12, incl. ED rows closed with evidence); all quiet-mac rows render GATED/BLOCKED; merged `47d2645` (#150). Residual for the seat: the gate's own clearance text is the standard THIS sitting is measured against |
| **F3 / B3** (should_fix per Disposition 3) — bifurcated authority | **STILL-OPEN (partial).** Done: `updated`, `latest_report`, D117-U11-IDPIN-PROJECTION and FLOOR-COMMONMODE-01 rows gone, P2-006 retired by ruling, REFREEZE-D147-CLOSE row added. Not done: the three named WOs were **not enrolled as kernel rows**; their hand-written sections persist at TASK_QUEUE.md:207/733/761 and were not demoted to pointers; **four further** hand-written WO sections now sit outside the markers, three with no kernel row (:293, :336, :363) |
| **F4 / S1** — D-118 gate ledger not mechanical | **STILL-OPEN.** Zero gate-ledger checker in `.github` or `scripts`; D-118's text still claims "MECHANICALLY CHECKED"; never scheduled into the verdict's should-fix batch |
| **F5 / S2** — kernel freshness false | **READY-evidence-attached, with a residual.** `updated: 2026-08-19`, `latest_report` = T12/T13. No automated staleness detector exists; freshness truth is still maintained by hand |
| **F6 / S3** — FREEZE-FCM01 banner unamended | **STILL-OPEN.** Banner byte-unchanged; no dated D-133 cl.4 supersession note; WO-L1-5 unexecuted |
| **F7 / N1** — `draft_status: unfrozen_draft` | **STILL-OPEN for `_v1` (permanently, by design); cured for `_v2`/`_v3`** (key absent). Nit-severity |
| **F8 / N2** — `gen_state.py:372` substring lint | **STILL-OPEN.** Unchanged. Nit-severity |
| **Baseline-manifest SUPERSESSION** (charter amendment 12; verdict Phase 3) | **STILL-OPEN — and now adversely evidenced.** Manifest unchanged since `694442c`; **no** `pack_digest_algorithm`, **no** per-binding paths; all three `_v1` `pack_digests` **fail to reproduce** at `b92b43d` (cause: `generate_configs.py` in each pack) |
| **Phase-3 focused re-audit of L1** | **STILL-OPEN — not started.** No re-audit artifact exists (see §5 probe 6) |
| **ED-QUAL-L1-1** (stable capability) | **ED-ROW OPEN.** No `verify`-subcommand production replay located; partially superseded in intent by R1's no-grandfathering ruling — needs re-scoping or an explicit ruling, not a silent close |
| **ED-QUAL-L1-2** (stable capability) | **ED-ROW: substantially closed with evidence, NOT formally closed.** Re-author + reissue + recommit executed on the production machine with custody; **Ed's exact-byte confirmation still owed**; no closure ledger entry exists anywhere |
| **PER-SEAT OVERALL** | **CANDIDATE: NOT-READY-as-assembled.** Two blocker-class items carry attached, mechanically verified repairs (B2 fully; B1 transformed but time-boxed and unmerged); four items (S1, S3, N1-`_v1`, N2) are untouched; the **baseline manifest is unsuperseded AND demonstrably stale**; the Phase-3 focused re-audit of this seat does not exist; both ED rows lack a closure record and the charter form requires ED-QUALIFICATION rows CLOSED WITH EVIDENCE. The seat rules |

---

## 5. WHAT A SKEPTICAL SEAT SHOULD PROBE

1. **(a) Stale-head attack — was any of this verified at the CURRENT head?**
   Run `git -C <tree> log --oneline -1` and compare to every head cited in the evidence chain.
   Known divergences to falsify against: the assembler brief says HEAD `4597ad4`, the tree is at
   `b92b43d`; the `_v3` U11 projection receipts bind `reviewed_git_commit:
   d59d36f50098c343af642a6bc24259247469d5a9`; the `_v3` evidence receipts bind `head_commit:
   1d3873bb7a37e9363202429f14587c85a0b4efc0`; the production measurement checkout
   `/Users/edr/JouleWise-measurement-20260818` is at `94dc3b34`, **10 commits behind** the branch
   head (`git rev-list --count 94dc3b34..HEAD` = 10, listed in §2). **Falsifier:** any arm-path
   predicate that requires the reviewed head to equal the receipt-bound head will refuse at
   `b92b43d`; conversely, if a repair was validated only at `1d3873b`/`d59d36f`, ten subsequent
   commits are unaudited for it.
2. **(b) Coverage / universe re-enumeration attack (standing packet element per
   `council-verdict.md:18-22`).** Do not accept L1's 24-item universe. Re-enumerate independently
   and specifically test whether the universe should now include artifacts that did not exist on
   2026-08-15: the three `_v3` packs (each 20 top-level entries incl. `arm_readiness.evidence/`,
   `arm_readiness.freeze.receipts/`, `identity_pin_projection.receipts/`), the R1 lifecycle
   registry placeholder path, `scripts/capture_t0_step.py` (landed via #152), the D-149 GO-receipt
   template `docs/process/d149-go-receipt-template.md`, and the four new hand-written TASK_QUEUE WO
   sections. **Falsifier:** if the re-enumerated denominator exceeds 24 while the numerator does
   not move proportionally, L1's coverage claim falls the way L2's did.
3. **The B1 repair is a clock reset, not a design change — test the recurrence directly.**
   Recompute: `python3 -c "import json,glob,ctypes; …"` over
   `configs/campaigns/*_v3/arm_readiness.evidence/*.json` reading top-level
   `valid_until_monotonic_ns`, and compare against live `CLOCK_UPTIME_RAW` and `sysctl -n
   kern.bootsessionuuid`. Assembler measurement: min `2468742407178458` vs live
   `2414989316822250` (≈14.9 h). Then read `joulewise/arm_readiness_evidence.py:42` and confirm
   `_EVIDENCE_VALIDITY_NS` is still 86,400 s, and confirm the receipts' `schema_version` is
   `joulewise.arm_readiness_evidence_receipt.v1` rather than the R1 split schemas of
   `docs/decision_log.md:9264-9268`. **Falsifier:** if headroom is under the seat's own arm-night
   budget at sitting time, or has lapsed, **B1 has recurred verbatim on the successor family** and
   the repair's evidence is self-invalidating.
4. **The manifest is dead — verify it, don't take this row's word.** Run
   `joulewise.arm_readiness.committed_pack_tree_sha256` over each `_v1` pack and diff against
   `docs/process/audit-baseline-manifest.json` `pack_digests`; then
   `git diff --stat ac3fe1d..HEAD -- configs/campaigns/<pack>`. **Falsifier:** all three digests
   mismatch (assembler result), the cause is a committed `generate_configs.py` change inside each
   frozen `_v1` pack, and the manifest's `invalidation_rule` therefore fires — so any L1 claim
   resting on the 2026-08-15 baseline is, on the manifest's own terms, void until supersession.
5. **Supersession-field compliance.** `python3 -c "import json;print(sorted(json.load(open('docs/process/audit-baseline-manifest.json'))))"`.
   **Falsifier:** absence of `pack_digest_algorithm` and of per-binding `path` fields means the
   verdict's `council-verdict.md:68-70` conditions are unmet even if a supersession is drafted at
   the sitting.
6. **(c) Self-reported repair with no independent audit — the S5 mint chain.** Every statement
   that the freeze-0003 receipts were verified comes from the implementing session:
   `RUN_STATE.md:169-171`, `docs/process/ed-s5-mint-decision-2026-08-19.md:66-69`, and the run
   report `docs/run_reports/2026-08-19-t12-t13-session.md`. Check whether any INDEPENDENT reader
   verified them: `ls docs/process_traces/2026-08-19-refreeze-execution/reports/` (assembler saw
   S0/S1 lens+delta reports, S2 goldens, S3 emission, consistency sweep, docs-fidelity — **look
   specifically for an S4 or S5 lens/delta report**). Also note `RUN_STATE.md:146-149`: the
   **D-144 BIG-design pre-merge seat pass over the implemented S0–S5 artifact is a ruled
   requirement that has NOT run** ("POOL-GATED (~23:22). This is a ruled requirement of
   D-146/D-147's own classification, not optional"), and `RUN_STATE.md:133-135`: both merge-gate
   inputs (final canonical; fresh-pass review) "were killed mid-run — **BOTH GATE INPUTS ARE
   UNSATISFIED** and must be rerun from scratch." **Falsifier:** if no independent audit of S4/S5
   exists, the entire B1 repair rests on the implementing session's self-grade — the exact posture
   `council-verdict.md:18-22` says does not entitle READY.
7. **Kernel single-authority regression test (B3).** Enumerate every `^## WO-` heading in
   `TASK_QUEUE.md` outside the marker fence (`:511` BEGIN / `:693` END) and intersect with
   `json.load(open('docs/process/state_kernel.json'))['tasks'].keys()`. Assembler result: 7
   hand-written WO sections, of which `WO-SAMPLER-SUPERVISOR`, `WO-CRASHMATRIX-RELIABILITY`,
   `WO-DETERMINISM-LOAD-ISOLATION`, `WO-MINT-ESTIMATOR-VOCAB`, `WO-COLLECTION-MARGIN-01`,
   `WO-ARM-EVIDENCE-AUTHOR-01` have **no kernel row**. **Falsifier:** the DOC-008 single-authority
   violation B3 identified is not merely unfixed — it grew by three new sections after the verdict,
   one of them registered 2026-08-19 (`WO-DETERMINISM-LOAD-ISOLATION`).
8. **Gate-clearance self-reference.** Read the installed gate's `clearance` string (quoted in §2)
   and confirm the sitting is being run against exactly that standard — "no NOT-READY, no
   UNVERIFIED, and **all ED-QUALIFICATION rows closed with evidence**". **Falsifier:** if any ED row
   in this packet (L1-1, L1-2, L5-1, and the other seats') is open, the kernel's own gate text
   says the gate does not clear, regardless of how the finding rows are graded.
9. **D-118 lint existence.** `grep -rniE "gate.?ledger" .github scripts` and read
   `docs/decision_log.md:143`. **Falsifier:** zero hits against a decision-log row that still says
   "MECHANICALLY CHECKED" — the prose-only enforcement L1-S1 named is intact and is the mechanism
   that would have to police this very sitting's merge.

---

## 6. OPEN ITEMS FROM THIS ROW

- **The audit-baseline manifest has not been superseded, and its three `_v1` pack digests no
  longer reproduce at `b92b43d`** (cause: a committed `generate_configs.py` change inside each
  frozen `_v1` pack between `ac3fe1d` and HEAD). The ruled supersession fields
  (`pack_digest_algorithm`; per-binding paths; chain-template coverage note) are absent.
- **Phase 3's focused re-audit of L1 does not exist.** No artifact under `docs/process_traces/`
  matches; the only post-verdict re-audit is `2026-08-15-l2-reaudit` (Phase-1 WO-L2-REAUDIT).
- **The B1 repair reproduces B1's mechanism:** `_v3` freeze evidence is the legacy
  `joulewise.arm_readiness_evidence_receipt.v1` schema with the unchanged 24 h
  `_EVIDENCE_VALIDITY_NS`, ≈14.9 h of headroom measured at probe time, death stated at
  ~2026-08-20T16:51Z or on any reboot.
- **The R1-ruled content-bound lifecycle is not in force for the frozen family:** no successor row
  registry is installed (`configs/arm_readiness/` holds only `d117_row_registry_v1.json`), the
  five Ed-reserved registry values are still at council (D-148.5), and the checked-in placeholder
  refuses issuance/consumption by design.
- **`WO-L1-1` … `WO-L1-5` were never enrolled as tracked rows** in TASK_QUEUE or the kernel; there
  is no per-work-order closure record for this seat.
- **WO-L1-4 (D-118 gate-ledger lint) is unexecuted and unscheduled** — neither built nor was D-118
  amended; L1-S1 was omitted from the verdict's Phase-1 should-fix batch.
- **WO-L1-5 (FREEZE-FCM01 dated supersession banner) is unexecuted** — the prohibition banner is
  byte-unchanged.
- **B3's demotion limb is unexecuted and the class regressed:** three post-verdict hand-written WO
  sections outside the generated region carry no kernel row
  (`WO-SAMPLER-SUPERVISOR`, `WO-CRASHMATRIX-RELIABILITY`, `WO-DETERMINISM-LOAD-ISOLATION`), and the
  three original sections were never demoted to pointers nor enrolled as kernel rows.
- **No automated staleness detector for `kernel.updated`** was built (L1's own unexecuted
  obligation); freshness is hand-maintained.
- **`gen_state.py:372` D-041 substring lint unchanged**; its sibling limb at `:371` still requires
  a `P2-006` task dependency after P2-006's retirement.
- **`draft_status: "unfrozen_draft"` is permanent in the `_v1` bytes** (`plan_tree.json:793`); the
  M-2 override therefore remains the operative instrument for `_v1` for its lifetime
  (`cold-fable-ruling.md:55` ruled the M-2 remedy "incomplete as recorded").
- **ED-QUAL-L1-1 has no located closure evidence** for the `verify`-subcommand production replay,
  and may be in tension with R1 cl.5's no-grandfathering prohibition — needs a ruling, not a
  silent close.
- **ED-QUAL-L1-2's Ed-side exact-byte confirmation is still owed**
  (`docs/process/ed-s5-mint-decision-2026-08-19.md:94-95`; `RUN_STATE.md:82-84`).
- **No independent audit of the S4/S5 mint execution was located**; the D-144 pre-merge seat pass
  over the implemented S0–S5 artifact is a ruled requirement that has not run, and both merge-gate
  inputs are recorded UNSATISFIED (`RUN_STATE.md:133-135, 146-149`).
- **Nothing in this repair program has merged to main** — `impl/r2-s0-mint-resolver` @ `b92b43d`;
  `RUN_STATE.md:138`: "NO MERGE HAS OCCURRED."
- **Provenance discrepancy:** the assembler brief states HEAD `4597ad4`; the tree is `b92b43d`.

---

## 7. ADDENDUM — the read-only tree MOVED during assembly (recorded, not graded)

All verifications in §§1–6 were executed at **`b92b43d`**. At the close of assembly
(`git -C wtS0 log --oneline -1`) the shared worktree had advanced to **`48f337b`**, three commits
later — a concurrent writer landed while this row was being assembled:

| Commit | Subject (verbatim) |
|---|---|
| `7305e0d` | Prep sprint: paper staging landed — registry audit (0/34 clean locators; 8-slot coverage hole; era-codes renderer gap F1), refreshed-registry DRAFT (anchors only), 5 STOP_FILL figure skeletons + drift-proof generator |
| `45e0229` | Fresh-pass gate CLEAN through b92b43d (report custodied); fix its B1/B2 + S1-S10 bookkeeping findings (kernel status_note, gate-record pinning, stale hazards/banners, gate-count unification, D-149 ONE-home, GO-evaluator queue row) |
| `48f337b` | README: restore the RUN_STATE freshness-owner pointer the banner rewrite dropped (cures the docs-freshness red pushed in 45e0229) |

**What this changes for L1 (verified by `git diff b92b43d..HEAD`):**
- **Unchanged:** `docs/process/audit-baseline-manifest.json` (still the single `694442c` version),
  `FREEZE-FCM01.md`, every `configs/campaigns/**` pack byte, `scripts/gen_state.py`,
  `.github/**`. Every §2 finding-level conclusion therefore still holds at `48f337b`.
- **Changed:** `docs/process/state_kernel.json` (7 lines). The `WINDOW-COUNCIL-GATE` record itself
  is **byte-unchanged**; what moved is the three window rows: `goal` now names the `_v3` packs
  (was `_v1`), and each `status_note` was shortened to "Successor family frozen (freeze-0003,
  2026-08-19); awaits READY-candidate council + D-149 GO conditions" — **dropping the previous
  explicit mention of the Phase-2 successor re-freeze and the Phase-3 re-audit fences.** A
  skeptical seat may wish to probe whether that shortening removes a truthful fence from the
  authority plane (L1's own subject matter) at exactly the sitting that would clear the gate.
- **Also changed:** `RUN_STATE.md`, `TASK_QUEUE.md`, `WINDOW_STATUS.md`, `README.md`,
  `docs/decision_log.md` (1 line), `tests/test_gen_state.py` (1 line), and a new custody file
  **`docs/process_traces/2026-08-19-prep-sprint/merge-freshpass.md`** (350 lines).
- **Directly affects ROW-L1 §5 probe 6:** the fresh-pass merge-gate input that `RUN_STATE.md:133-135`
  recorded as UNSATISFIED is now claimed **CLEAN through `b92b43d`** with a custodied report at
  `docs/process_traces/2026-08-19-prep-sprint/merge-freshpass.md`. The seat should read that report
  directly and check (i) whether it covers the L1-bearing commits, (ii) whether it is
  self-reported by the same session that authored the work, and (iii) that it does **not** cover
  `45e0229`/`48f337b`, which landed after its own coverage cutoff.
