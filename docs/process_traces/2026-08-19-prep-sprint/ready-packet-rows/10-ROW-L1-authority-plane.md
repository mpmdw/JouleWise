# ROW L1-AUTHORITY-PLANE — control/authority plane (GATING)
Original verdict: NOT-READY (3 blockers / 3 should-fix / 2 nits / coverage 20/24)
Not flagged UNVERIFIED on coverage at the sitting (only L2 was) — but see the COVERAGE sub-row:
the council ruled the whole work-order program **NOT CERTIFIED COMPLETE** because every seat's
evidence universe was self-nominated (council-verdict.md §VERDICT ¶3).

**Assembly conditions (state them to the seat).** Repo worktree `wtS0`, branch
`impl/r2-s0-mint-resolver`. The brief pinned HEAD `d10881b`; the branch **advanced during
assembly** and this row was verified at HEAD **`b92b43d`** ("Shakedown-v3 first-light run card",
2026-08-19 18:50 PDT), 51 commits ahead of `main`/`origin/main` = `0099382`. Live boot session
`DA90818C-9C31-45D0-8813-DEAE65FBA143` (unchanged since the 2026-08-13 freeze night).
The branch kept advancing while this row was written (observed `7305e0d` at file-write time) —
every sha below should be re-pinned to the sitting head before it is relied on.

---

## L1-B1 — Frozen packs cannot arm: all 33 freeze evidence receipts monotonically lapsed

### (a) Original finding (VERBATIM)
> ### L1-AUTHORITY-PLANE B1: Frozen packs cannot arm: all 33 freeze evidence receipts have lapsed their monotonic validity on the un-rebooted arming machine
> at: configs/campaigns/*/arm_readiness.evidence/*.json; joulewise/arm_readiness.py:3710-3717,3948-3955
> scenario: Ed attempts tonight's slipped Window ALPHA arm: generate_arm_receipt authenticates the pack freeze evidence (boot session matches — no reboot occurred), but the arm receipt's valid_until is min-inherited from evidence expirations that are already in the past (earliest 1986799611717708 ns vs live ~1997.9e12 ns), so verify_arm_receipt refuses readiness_record_expired and consume_launch_capability can never fire. The direction is correctly fail-closed, but the funded window is unlaunchable under the audited bytes; the recorded standing constraint ('NO REBOOT before T-0 or the evidence re-authors') is insufficient — no reboot happened and the capability still died of monotonic age from the window slip. Remedy (re-author evidence, reissue freeze receipt, re-pin plan tree, recommit) changes pack bytes, rotates the committed pack digests, and voids the audit-baseline manifest's pack digests under charter amendment 12 — the council must schedule this re-freeze before or at GO.

Citation: `sitting-packet-FINAL.md` §3 "L1-AUTHORITY-PLANE B1"; seat report
`docs/process_traces/2026-08-15-readiness-council/seat-reports/L1-AUTHORITY-PLANE-report.md` §5 B1
and §3 negative probe 6; refuter verdicts `refuter-outputs/refuter-verdicts.md` §A-contract
("L1-B1 expiry: CONFIRMED. Remedy corrected: in-place re-author NOT contract-valid (D-131 requires
successor pack+custody root)") and §A-execution ("F1 (expiry) CONFIRMED executed: 33/33 generic
receipts refuse readiness_record_expired").
Post-verdict adjudication: not struck. Routed to **Phase 0 R1** (freeze-evidence lifecycle ruling,
own cold gate) then **Phase 2** (re-freeze once, atomically, last among pack-byte changes).

### (b) What changed since 2026-08-15

**Ruling layer (on main).**
- `docs/decision_log.md:9196` — **R1 RULED** (magistrate synthesis of the rule-11 cold gate,
  2026-08-15): content-bound lifecycle ADOPTED with the taxonomy split
  RE_DERIVABLE / EXECUTION_BOUND / TIME_BOUND / SESSION_STATE_BOUND / TEMPORAL_CAPABILITY.
  Clause 5 is directly on point: *"NO GRANDFATHERING (both seats + contract text): the 33 expired
  v1 receipts are never revalidated; migration is fresh re-authoring within the Phase-2 successor
  family, one atomic family transaction."* Gate record:
  `docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/`.
  WHERE it lives: **merged to main** (R1 implementation amendments at `decision_log.md:9252`,
  `:9320`).
- Code: `joulewise/arm_readiness.py:676-711` `R1_EVIDENCE_FRESHNESS_CLASSES` (code constant, one
  class per evidence kind) + `validate_r1_class_lifecycle` (`:3344-3403`) +
  `validate_r1_temporal_budget` (`:3299-3341`). Landed by `9e71279` "Fix round 1 (both lens sets):
  … class assignments code-constant with registry validate-only + production-path lifecycle
  enforcement (TIME_BOUND bypass dead)". WHERE it lives: **merged to main**.
  What it does: pack-side kinds (PACK_AUTHENTICATION, ESTIMATOR_IDENTITY, MINT_TRUST,
  MULTICELL_MINT, RECEIPT_ORACLE, RECOVERY_LEDGER_TEST, REASON_CODE_COVERAGE,
  THREE_WINDOW_REGRESSION, ACCEPTANCE_OWNER) are `EXECUTION_BOUND`; DOCTRINE_PIN and PACK_FAMILY
  are `RE_DERIVABLE`. **EXECUTION_BOUND still enforces boot + monotonic horizon** — R1 clause 1
  explicitly RETAINS it "until Ed's execution-environment-fingerprint ruling lands".

**Execution layer (branch-only).** The D-147 Phase-2 transaction minted a `_v3` successor family
with freshly authored evidence:
- `1d3873b` "S3: d117 _v3 pack family emitted via unedited _v2 generators, bound to r6 at birth"
  (first appearance of `configs/campaigns/d117_floor_qwen25_1p5b_v3/`).
- freeze-0003 receipts: `5e38f1e` (1p5b_v3), `eb7f6c6` (7b_v3), `94dc3b3` (contrast_v3),
  `8b2b021` (S5 confirmation table in `docs/process/ed-s5-mint-decision-2026-08-19.md`).
- WHERE they live: **branch-only** (`impl/r2-s0-mint-resolver`). Verified: `git ls-tree main
  --name-only configs/campaigns/` lists `_v1` and `_v2` families only — **no `_v3` pack exists on
  main**. D-147 (`decision_log.md:170`) is the governing ruling.
- `configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json`:
  `schema_version joulewise.arm_readiness_freeze_receipt.v2`, `status PASS`, 14 rows,
  `refusals: []`, `arm_disposition NOT_APPLICABLE`, `predecessor.freeze_receipt = freeze-0002`
  (sha `1277103b…`), `predecessor.pack_sha256 95f7c51c…`, `pack_identity.pack_root =
  /Users/edr/JouleWise-measurement-20260818/…` (a NEW measurement checkout).

**Executed measurement of the actual expiry state** (this assembler, at
`measured_at_utc 2026-08-20T02:00:47Z`, `time.monotonic_ns() = 2415296389563083` — the same clock
the code uses, `arm_readiness.py:6499`, `:6325`):

| family | receipts | min `valid_until_monotonic_ns` | remaining |
|---|---|---|---|
| `_v1` (the audited packs) | 33 | 1986799611717708 | **−119.0 h (expired)** |
| `_v2` | 33 | 2370023883623625 | **−12.6 h (expired)** |
| `_v3` (the operative family) | 33 | 2468742407178458 | **+14.85 h (LIVE)** |

All 33 `_v3` receipts carry `boot_session_id da90818c-9c31-45d0-8813-deae65fba143`, which equals
the live `kern.bootsessionuuid`.

**What did NOT change:** the min-inheritance mechanism the finding names.
`joulewise/arm_readiness.py:6230-6242` still computes
`valid_until = min([evaluated_at_monotonic_ns + arm_horizon_ns, *evidence_expirations])`.
The `_v3` family reset the clock; it did not remove the clock.

### (c) Candidate disposition for the seat
**STILL-OPEN (evidence attached; conditionally cured with a running fuse).**
The seat is adjudicating whether a launch capability that exists only inside a ~15-hour,
branch-only, single-boot-session window — on a pack family that is not on `main`, under a
mechanism (min-inheritance of EXECUTION_BOUND horizons) that R1 deliberately retained — satisfies
a READY-candidate row, or whether B1's defect class simply recurs on the next slip.

### (d) Skeptical probes
1. Re-measure now: `python3 -c "import json,glob,time; now=time.monotonic_ns(); print(min(json.load(open(f))['valid_until_monotonic_ns'] for f in glob.glob('configs/campaigns/*_v3/arm_readiness.evidence/*.json')) - now)"` — is the `_v3` horizon still positive at the moment of the sitting? At assembly it had **14.85 h** left and was shrinking in real time.
2. `sysctl -n kern.bootsessionuuid` — if it is no longer `DA90818C-…`, every `_v3` receipt is dead on boot binding, not just horizon, and B1 is fully live again.
3. `git ls-tree main --name-only configs/campaigns/` — confirm the `_v3` family is still absent from `main`. The shakedown run card (`docs/process/window-run-cards/shakedown-v3-first-light.md`, `b92b43d`) itself requires "the merge wave has landed on main (the window must run frozen-main bytes, not a branch)". Does a READY-candidate row rest on unmerged bytes?
4. Read `joulewise/arm_readiness.py:6230-6242` — confirm the arm receipt still min-inherits evidence expirations. If so, what governed lane RE-AUTHORS the `_v3` evidence when the horizon lapses? R1 clause 5 bars revalidation and D-131 requires a successor pack + custody root, i.e. a `_v4` family — is that lane written down anywhere?
5. `configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.evidence/evidence-doctrine-pin.json` carries BOTH `boot_session_id` and `valid_until_monotonic_ns`, yet DOCTRINE_PIN is classed `RE_DERIVABLE`, and `validate_r1_class_lifecycle` (`arm_readiness.py:3366-3371`) raises `readiness_schema_invalid` — *"RE_DERIVABLE evidence may not store boot or deadline validity"*. Which code path actually authenticates these receipts at arm, and does the R1 class validator run on them at all? (All 33 `_v3` receipts are still `schema_version joulewise.arm_readiness_evidence_receipt.v1`, the generic schema the R1 amendment at `decision_log.md:9320` calls a `V1_GRANDFATHERING` refusal role on R1-registry paths.)
6. The `_v3` receipts record `head_commit 1d3873bb…` while HEAD is `b92b43d`. Prove from code whether freeze evidence is head-bound at arm; L5's audit asserts the chain "binds plan+evidence+boot rather than head" — verify, don't inherit.
7. The audit-baseline manifest (`docs/process/audit-baseline-manifest.json`) still pins `head_commit ac3fe1d2…` and the `_v1` pack digests; last touched by `694442c`. Charter amendment 12 / council Phase 3 require a SUPERSESSION manifest with `pack_digest_algorithm` and paths for all bindings. It does not exist. Can any row be READY against a baseline that no longer describes the operative packs?

---

## L1-B2 — Work-selection state fails open: no council gate in the kernel; superseded P2-006 renders READY [QUIET-MAC]

### (a) Original finding (VERBATIM)
> ### L1-AUTHORITY-PLANE B2: Authoritative work-selection state fails open for quiet-window selection: no council gate, and a superseded campaign renders READY [QUIET-MAC]
> at: docs/process/state_kernel.json (active_global_gates: []); RUN_STATE.md:3433
> scenario: A successor session or tired operator obeys RUN_STATE's generated region, which today renders 'READY — Q2 P2-006: Window A two-model campaign' with zero active global gates — despite Ed's 2026-08-13 window-gating directive (windows sit behind the council verdict) and despite D-117 having superseded the Window-A program. A quiet night gets spent on a campaign whose outputs do not trace to the current claim path, bypassing the council gate entirely, because the gate exists only in decision-log prose while the kernel's purpose-built gate machinery (proven working by probe) carries no gate row. The actual funded program (three frozen D-117 packs) has no kernel row at all.

Citation: `sitting-packet-FINAL.md` §3 "L1-AUTHORITY-PLANE B2"; seat report §5 B2 and §3 negative
probe 7 (gate positive control); refuter verdicts `refuter-outputs/refuter-verdicts.md`
§DG-contract ("L1-B2 kernel fail-open: PARTIAL->survives as blocker … refuted portion: D-117 does
not formally retire P2-006 — needs a ruling, not deletion") and §DG-execution ("L1-B2: CONFIRMED
blocker … data gap not machinery gap").
Post-verdict adjudication: routed to Phase 0 **R3** + Phase 1 **WO-KERNEL-RECONCILE**
(magistrate-supervised, lieutenant-forbidden alone).

### (b) What changed since 2026-08-15
- `cd4c136` "R3 (council Phase 0): P2-006 formally retired from window selection by supersession;
  executes via WO-KERNEL-RECONCILE" — body at `docs/decision_log.md:9037`. Retirement is
  **supersession, not deletion**; any future two-model exploratory campaign enters as a NEW row.
  WHERE it lives: **merged to main**.
- `47d2645` "WO-KERNEL-RECONCILE: council gate installed, P2-006 retired (R3), kernel truth pass
  (one transaction) (#150)" — PR **#150**, files: `RUN_STATE.md`, `TASK_QUEUE.md`,
  `docs/process/state_kernel.json` (+759/−…), `tests/test_gen_state.py`. Commit body records
  D-121 terminal review at delta-audited head `b887d5b`, `gen_state --check` green, full CI green
  including both crash-matrix jobs. WHERE it lives: **merged to main**.
- Verified in the current bytes at HEAD `b92b43d`:
  - `docs/process/state_kernel.json` → `active_global_gates` contains exactly one entry,
    `id: WINDOW-COUNCIL-GATE`, `scope: {lanes: [quiet_mac], operation: select}`,
    `allowed_task_ids: []`, authority = the 2026-08-13 window-gating directive **and**
    `docs/process_traces/2026-08-15-readiness-council/council-verdict.md#verdict`, clearance =
    charter amendments 11-12 ("a reconvened READY-CANDIDATE council verdict records no NOT-READY,
    no UNVERIFIED, and all ED-QUALIFICATION rows closed with evidence").
  - `P2-006` **has no task row** in the kernel (73 tasks; `git show 47d2645 -- state_kernel.json`
    shows `- "P2-006": {` at diff line 548). Three surviving dependencies now target the
    placeholder `P2-006-SUCCESSOR-ROW` (kernel lines 1933, 2037, 2090), state `pending`.
  - RUN_STATE generated region (`RUN_STATE.md:4038-4072`) now renders an
    "Active Global Work-Selection Gates" section and, in [QUIET-MAC]:
    `GATED — Q2 D117-W-ALPHA (excluded by: WINDOW-COUNCIL-GATE)`. No READY quiet-mac row.
  - The funded program now HAS kernel rows: `D117-W-ALPHA` (queued), `D117-W-BETA` (blocked),
    `D117-W-GAMMA` (blocked), plus `REFREEZE-D147-CLOSE` (active).
- `0e96dbb` "D-149: standing conditional T-0 GO — full no-hands window automation (Ed); kernel
  fences updated (regen + pins green)" adds a D-149 fence to `D117-W-ALPHA`:
  *"No arm or collection before a READY-candidate council verdict and the separate perishable T-0
  GO; T-0 GO auto-issues per D-149 when its five recorded conditions pass (no-hands windows)…"*.
  WHERE it lives: **branch-only**.
- `75cb868` "S6 bookkeeping: kernel transaction (window rows -> _v3, REFREEZE-D147-CLOSE row,
  latest_report; regen + test pins)". WHERE it lives: **branch-only**.
- Executed at HEAD in a clean clone: `python3 scripts/gen_state.py --check` → **exit 0**;
  `python3 -m unittest tests.test_gen_state` → **40 tests OK**.

### (c) Candidate disposition for the seat
**READY-EVIDENCE-ATTACHED.** The named data gap is closed by a ruled, merged, magistrate-supervised
transaction: the gate exists in the kernel, P2-006 has no live row, the funded packs have rows, and
the render is GATED. The seat is adjudicating (i) whether the gate's own clearance condition is
what this sitting is being asked to satisfy — i.e. the gate is self-referentially the thing under
adjudication — and (ii) the D-142 precedent below.

### (d) Skeptical probes
1. `python3 -c "import json;print(json.load(open('docs/process/state_kernel.json'))['active_global_gates'])"` at the sitting head — one gate, `allowed_task_ids: []`, scope quiet_mac/select?
2. **D-142 carve-out precedent** (`docs/decision_log.md:165`): a diagnostic shakedown ran on 2026-08-18 *while WINDOW-COUNCIL-GATE was live*, under Ed's standing night license, on the reading that "the gate binds CLAIM windows and kernel tasks". The counter-reading ("gate text names no shakedown carve-out") is preserved in the T10 report's B-5. Does a gate that has already been read past once still fail closed?
3. `grep -n "P2-006" docs/process/state_kernel.json` — the only hits are `P2-006-SUCCESSOR-ROW` dependency targets with `evidence: null, state: pending`. Does a dependency on a task ID that has no row validate, and does `gen_state.py` refuse dangling targets? (Invariant list at `scripts/gen_state.py:368-373`.)
4. Re-run the seat's own positive control in reverse: remove the gate in a scratch copy and confirm a quiet-mac row becomes selectable — i.e. the render's GATED state is produced by the gate, not by the row's own dependencies.
5. `D117-W-ALPHA`'s `goal` string still reads *"the frozen ALPHA pack **d117_floor_qwen25_1p5b_v1**"* while its `acceptance.evidence[0]` reads *"Exact frozen pack **d117_floor_qwen25_1p5b_v3**"* (both in `docs/process/state_kernel.json`, after `75cb868`'s "window rows -> _v3"). Is the kernel telling the truth about which pack the funded window runs?

---

## L1-B3 — Bifurcated work-selection authority (severity ruled DOWN to should_fix)

### (a) Original finding (VERBATIM)
> ### L1-AUTHORITY-PLANE B3: Work-selection authority is bifurcated: launch-blocking work orders live as hand-written prose outside the generated region while kernel rows assert falsehoods
> at: TASK_QUEUE.md:201,635,659 (outside markers 452-613); docs/process/state_kernel.json /tasks/D117-U11-IDPIN-PROJECTION
> scenario: WO-MINT-ESTIMATOR-VOCAB, WO-COLLECTION-MARGIN-01, and WO-ARM-EVIDENCE-AUTHOR-01 ('LAUNCH-BLOCKING for any window night') were 'registered in TASK_QUEUE' as hand-written sections outside the marker-fenced generated region — invisible to gen_state --check and absent from the kernel, violating DOC-008's single-authority contract. Simultaneously the kernel's D117-U11-IDPIN-PROJECTION row still reads 'queued... Checked-in packs remain unprojected' at a head whose packs carry PASS projection and freeze receipts, and FLOOR-COMMONMODE-01 renders 'READY [AGENT]' despite its D-133 desk-thread disposition. A session trusting the declared AUTHORITATIVE_WORK_SELECTION_STATE misses launch-blocking obligations or resumes disposed work; a session trusting the prose contradicts the kernel.

Citation: `sitting-packet-FINAL.md` §3 "L1-AUTHORITY-PLANE B3"; seat report §5 B3.
**Post-verdict adjudication (NOTE):** `council-verdict.md` ADJUDICATED DISPOSITIONS §3 —
*"**L1-B3 severity — should_fix**, remedy subsumed into the blocker-gated kernel-reconciliation
transaction (cold §D; discharges Opus S10). P2-006 is retired only by formal ruling, never silent
deletion."* Split lenses: DG-contract reduced it to should_fix ("all three 'missing' WOs are
ancestors of HEAD — stale registration prose, not live blockers … Remedy: one kernel
reconciliation transaction; do NOT re-register shipped WOs"); DG-execution called the
authority-drift core a blocker; the magistrate synthesized rather than majority-voted.

### (b) What changed since 2026-08-15
- `47d2645` (PR #150, **merged to main**) executed the single reconciliation transaction. Verified
  removals in `git show 47d2645 -- docs/process/state_kernel.json`:
  `- "D117-U11-IDPIN-PROJECTION": {` (diff line 230) and `- "FLOOR-COMMONMODE-01": {` (diff line
  449). Neither ID exists in the kernel's 73 tasks at HEAD — the false rows were **removed**, per
  the refuter's "do NOT re-register shipped WOs" remedy, not corrected in place.
- The three named work orders remain hand-written sections **outside** the generated region, now
  marked COMPLETED, at `TASK_QUEUE.md`:
  `## WO-MINT-ESTIMATOR-VOCAB — COMPLETED (e11b1ad, 2026-08-12…)` (line 207),
  `## WO-COLLECTION-MARGIN-01 — COMPLETED (1092984, 2026-08-12…)` (line 733),
  `## WO-ARM-EVIDENCE-AUTHOR-01 — COMPLETED (ac3fe1d, 2026-08-14…)` (line 761).
  Generated region markers are now `TASK_QUEUE.md:511-693`. None of the three has a kernel row.
  WHERE it lives: **merged to main** (the TASK_QUEUE edits ride `47d2645`).
- `gen_state --check` exit 0 and `tests.test_gen_state` 40 OK at HEAD (executed, clean clone).

### (c) Candidate disposition for the seat
**SUPERSEDED-BY-RULING + READY-EVIDENCE-ATTACHED.** Severity was ruled to should_fix at the
sitting and the ruled remedy (one kernel reconciliation transaction) has landed on main. The seat
is adjudicating whether "remove the false rows and leave the completed WOs as prose" discharges
DOC-008's single-authority contract, or merely relocates the bifurcation.

### (d) Skeptical probes
1. `grep -n "^## WO-" TASK_QUEUE.md` — how many hand-written WO sections now sit outside markers 511-693, and is any of them still open (not COMPLETED/CLOSED)?
2. Kernel row `DOC-008` is still `partial` (`state_kernel.json /tasks/DOC-008`). Is the single-authority contract itself an open obligation being cited as satisfied?
3. `git show 47d2645 --stat` — 815 insertions / 465 deletions across kernel + TASK_QUEUE + RUN_STATE + tests in ONE commit. Was every removed row's disposition recorded somewhere durable, or did removal erase the audit trail the R3 ruling insisted on ("supersession, not deletion") for P2-006 but perhaps not for FLOOR-COMMONMODE-01 / D117-U11-IDPIN-PROJECTION?
4. `TASK_QUEUE.md:491` "WO-LAUNCH-BINDING stage checkpoint — 2026-08-15" is hand-written prose asserting branch state for an **open** kernel row (`WO-LAUNCH-BINDING`, status `queued`). Is that the same failure mode the finding named, still live?

---

## L1-S1 (should_fix) — D-118's "mechanical enforcement" of the merge gate ledger does not exist

### (a) Original finding (VERBATIM)
> - [should_fix] [L1] D-118's 'mechanical enforcement' of the merge gate ledger does not exist anywhere in the repo

Seat-report text (VERBATIM, `L1-AUTHORITY-PLANE-report.md` §5 S1):
> **S1 (should_fix) — D-118's "mechanical enforcement" of the gate ledger does not exist** (no checker in .github/ or scripts/); merge gating is agent discipline — the prose-only failure mode D-118's own trigger recorded.

Citation: `sitting-packet-FINAL.md` §4 (should-fix titles); seat report §5 S1; work order WO-L1-4
(seat report §6); `triage.json:96,131`.
Post-verdict adjudication: none; folded into the council's Phase-1 "should-fix batch".

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** Searched: `grep -rn "D-118" scripts .github joulewise tests` → **zero
  hits**. `grep -rln "D-118" .` returns only prose surfaces (`TASK_QUEUE.md`, `RUN_STATE.md`,
  `docs/decision_log.md`, `docs/council_log.md`, run reports, process traces).
- `docs/decision_log.md:143` — the D-118 index row still reads *"…and MECHANICALLY CHECKED via a
  per-PR gate ledger; D-072 self-merge is conditioned on that ledger being complete…"*. Neither
  remedy branch of WO-L1-4 (build the lint **or** amend the clause) was executed.
- No new workflow file: `.github/workflows/` still carries `ci.yml` and
  `d117-production-proof.yml` on the audited paths; no gate-ledger lint job.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND / STILL-OPEN.** The seat is adjudicating whether a should-fix whose subject is
the *merge gate itself* may remain open while this branch's 51 unmerged commits queue for a merge
wave that D-148 clause 2 declares "gate-authorized, not Ed-authorized".

### (d) Skeptical probes
1. `grep -rn "gate.ledger\|gate_ledger" .github scripts` — still nothing?
2. `docs/decision_log.md:143` — read the D-118 row aloud at the sitting; is the repo's own decision log asserting a mechanism that does not exist, at a sitting whose product is a merge authorization?
3. D-148 clause 2 (`decision_log.md:171`) pre-authorizes the impl→integration→main wave "on gates-green". Which artifact records that the gate ledger is complete for this wave, and who checks it?

---

## L1-S2 (should_fix) — kernel.updated and latest_report are false, with no invariant forcing them to move

### (a) Original finding (VERBATIM)
> - [should_fix] [L1] kernel.updated and latest_report are false, and no invariant forces them to move

Seat-report text (VERBATIM, §5 S2):
> **S2 (should_fix) — kernel.updated (2026-08-08) and latest_report (T3, 2026-08-09) are false**, and only date-format is validated; the render carries a false freshness signal.

Citation: `sitting-packet-FINAL.md` §4; seat report §5 S2 and §2 ("The `updated`-field truth check
is manual; no automated staleness detector was built"); WO-L1-3 (seat report §6).

### (b) What changed since 2026-08-15 — DATA cured, MECHANISM not
- **Data (branch-only):** `75cb868` "S6 bookkeeping: kernel transaction (… latest_report; regen +
  test pins), T12/T13 run report". At HEAD `b92b43d`:
  `kernel.updated = "2026-08-19"`; `kernel.latest_report.path =
  "docs/run_reports/2026-08-19-t12-t13-session.md"` — the file exists and is the newest entry in
  `docs/run_reports/` (verified by `ls -t`). WHERE it lives: **branch-only**.
  (`47d2645` on main bumped these earlier in the same lineage.)
- **Mechanism: NO-REPAIR-FOUND.** `scripts/gen_state.py:216-218` still validates only the date
  FORMAT (`DATE_RE.match`) plus `_check_pointer` (`:131-141`), which asserts the pointer target
  *file exists* — nothing compares `updated` to the commit date, and nothing asserts
  `latest_report` is the newest report. No staleness detector was built.

### (c) Candidate disposition for the seat
**STILL-OPEN (data current, invariant absent).** The seat is adjudicating whether a freshness
signal that is true today by hand, on a branch, with no invariant behind it, closes a finding whose
substance was *"no invariant forces them to move"*.

### (d) Skeptical probes
1. `python3 -c "import json;k=json.load(open('docs/process/state_kernel.json'));print(k['updated'],k['latest_report'])"` at the sitting head vs `git log -1 --format=%ad` — do they agree?
2. `sed -n '210,220p' scripts/gen_state.py` — confirm the only `updated` check is `DATE_RE.match`.
3. Falsify: in a scratch copy set `updated` to `2026-01-01` and run `gen_state.py --check`. Exit 0 = the finding is untouched.
4. These values live only on the branch. If the merge wave slips, does `main`'s kernel go stale again while the render claims currency?

---

## L1-S3 (should_fix) — FREEZE-FCM01.md's standing prohibition never amended after D-133 cl.4

### (a) Original finding (VERBATIM)
> - [should_fix] [L1] FREEZE-FCM01.md's standing prohibition was never amended after D-133 cl.4 executed the re-spec

Seat-report text (VERBATIM, §5 S3):
> **S3 (should_fix) — FREEZE-FCM01.md's prohibition banner ("Do not… register in any pack"; "only Ed may relicense") was never annotated after D-133 cl.4 EXECUTE**, while the packs lawfully register the estimator; the repo's own dated-supersession convention was not applied.

Citation: `sitting-packet-FINAL.md` §4; seat report §5 S3 + §1 item 22; WO-L1-5 (seat report §6);
`triage.json:97,143-144`.

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND on the banner.** `git log --oneline -- FREEZE-FCM01.md` → a single commit,
  `60d9e42` (2026-08-11, pre-council). The file's lines 1-6 still read
  *"**State:** FROZEN at db3e212 … **Only Ed may relicense further work.** Do not fix, do not
  consume, do not register in any pack."* No dated supersession banner; `grep -n "D-133"
  FREEZE-FCM01.md` → no hit.
- **Adjacent, partial:** the kernel's `FLOOR-COMMONMODE-01` row (which rendered READY [AGENT]
  against the D-133 disposition) was **removed** by `47d2645` (**merged to main**), so the
  contradiction no longer renders in RUN_STATE/TASK_QUEUE — but the standing prohibition document
  itself is unamended.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND / STILL-OPEN.** The seat is adjudicating a live document that prohibits exactly
what the frozen packs do (register the common-mode estimator), while the only change made was to
delete the row that surfaced the contradiction.

### (d) Skeptical probes
1. `git log --oneline -- FREEZE-FCM01.md` — one commit, `60d9e42`, dated 2026-08-11. Unchanged?
2. `grep -rn "estimator_registration\|d124_two_shared_edge_common_mode" configs/campaigns/d117_floor_qwen25_1p5b_v3/` — do the operative `_v3` packs register the estimator the banner forbids?
3. Who now owns FLOOR-COMMONMODE-01's disposition, given its kernel row was deleted rather than dispositioned? Is there a decision-log entry recording the deletion's authority?

---

## L1-N1 (nit) — Frozen pack bytes still carry draft_status 'unfrozen_draft' (M-2)

### (a) Original finding (VERBATIM)
> - [nit] [L1] Frozen pack bytes still carry draft_status 'unfrozen_draft' — the M-2 scoped override remains the operative instrument indefinitely

Seat-report text (VERBATIM, §5 N1):
> **N1 (nit) — plan_tree.json:793 `draft_status: "unfrozen_draft"` persists in frozen bytes**; no code consumer (verified); the M-2 scoped override is now permanent for these packs.

### (b) What changed since 2026-08-15
- **Ruling (merged to main):** `docs/decision_log.md:173` **D-140** — "FREEZE-STATUS BYTE
  SEMANTICS, SUCCESSOR EXTENSION (cold gate 2026-08-18, composed verdict:
  `docs/process_traces/2026-08-18-freeze-semantics-coldgate/14-composed-verdict.md`, three seats
  concurring)": receipts-govern-over-descriptive-bytes EXTENDED to ALL successor packs by its own
  authority; *"'Freeze-aware' status = dynamic `target_status` from the authenticated attachment +
  the fail-closed non-preserve guard + option-(d) freeze-neutral emitted wording (round 6/7:
  `as_generated_pre_d134_freeze` + authority-naming fields)"*. Trace commit `3f9d759`
  (**merged to main**).
- **Bytes:** `grep -rn "draft_status" configs/campaigns/*/plan_tree.json` →
  `_v1` packs: `"unfrozen_draft"` (unchanged); `_v2` and `_v3` packs:
  `"as_generated_pre_d134_freeze"`. Introduced by `6d66439` (`_v2`, on main) and `1d3873b`
  (`_v3`, branch-only).
- **Executed** (clean clone at `b92b43d`):
  `python3 configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py --check --preserve-current-frozen-bytes`
  → `verified d117_floor_qwen25_1p5b_v3 frozen by d134 receipt: 100 science configs; …` (exit 0).
  The `_v1` generator still prints `verified unfrozen draft: 100 science configs; …`.
- **M-2 status:** the M-2 GATE AMENDMENT (`decision_log.md:9406`, merged) clause (c) says
  retirement occurs at successor freeze ONLY IF the Phase-2 generator work makes draft_status
  freeze-aware; clause (d) caps M-2's scope at the three 2026-08-13 receipt hashes.

### (c) Candidate disposition for the seat
**READY-EVIDENCE-ATTACHED for the operative `_v3` family; STILL-OPEN for the `_v1` packs.**
The seat is adjudicating whether M-2's retirement condition is met (the successor family emits
freeze-neutral bytes and the status line is dynamic), given that the `_v3` family is branch-only
and the `_v1` packs still carry the literal the finding names.

### (d) Skeptical probes
1. Run the three `_v3` generators with `--check` and **no** flags. At assembly all three refused: `generation failed: the current frozen identity requires preserve mode` (see the L5 row's F-4/F-2 probes). Does the seat's freeze-awareness evidence depend on a non-default invocation?
2. `grep -n "CURRENT_FROZEN_RECEIPT_SHA256" configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:75-77` → `1277103b…` (the **freeze-0002** sha) while the `_v3` plan_tree attachment names freeze-0003 (`0abfddb1…`). Is `target_status` derived from the authenticated attachment, or from a stale constant?
3. `grep -rn "draft_status" configs/campaigns/*_v1/plan_tree.json` — still `unfrozen_draft`. Does the D-140 extension retire M-2 for packs whose bytes were never re-emitted?

---

## L1-N2 (nit) — gen_state invariant 8's D-041 authority binding is a label-substring match

### (a) Original finding (VERBATIM)
> - [nit] [L1] gen_state invariant 8's D-041 authority binding is a label-substring match

Seat-report text (VERBATIM, §5 N2):
> **N2 (nit) — gen_state.py:372 binds post-2M authority by label substring** ("D-041" in label) — lint-grade only.

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** At HEAD `b92b43d`, `scripts/gen_state.py:368-373`:
  ```
  # Invariant 8: blocked_post_2m needs a P2-006 dependency; P2-022/P2-023 cite D-041.
  …
  if tid in ("P2-022", "P2-023") and "D-041" not in task["authority"]["label"]:
      fail(f"{where}: post-2M authority must resolve to D-041")
  ```
  Still a substring test on a free-text label. **Note the comment is now stale in a second way:**
  it says "blocked_post_2m needs a **P2-006** dependency" and P2-006 has been retired from the
  kernel by R3/`47d2645`.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND / STILL-OPEN**, with a new adjacent defect: the invariant's own comment cites a
retired row. The seat is adjudicating a nit that the kernel-reconciliation transaction touched
without updating.

### (d) Skeptical probes
1. `sed -n '365,375p' scripts/gen_state.py` — substring match still present; comment still names P2-006.
2. In a scratch copy, set `P2-022`'s authority label to `"not D-041 at all, mentions D-041 in passing"` and run `--check`. Exit 0 = binding is cosmetic.
3. Does invariant 8's `blocked_post_2m` clause still resolve now that P2-006 has no row — or is it silently vacuous? (`tests/test_gen_state.py` was rewritten by `47d2645`, +239/−… lines; does any test still exercise this branch?)

---

## L1-COVERAGE — 20 of 24 evidence-universe items examined; universes self-nominated

### (a) Original finding (VERBATIM)
Seat verdict table (`sitting-packet-FINAL.md` §2): `| L1-AUTHORITY-PLANE | GATING | NOT_READY |
20/24 | 3 | 3 | 2 | 7 | 5 | 2 |`.

Seat report §2 (VERBATIM):
> **20 of 24** items examined (2 partial: identity_pins internals, evidence_t0 internals; 2 not read: arm_readiness_evidence.py line-level, reserve_calibration_window_bracket.py). Unexecuted obligations, plainly:
>
> - joulewise/arm_readiness_evidence.py not read line-by-line (its outputs were authenticated via the replay code and executed suites, not its authoring logic).
> - scripts/reserve_calibration_window_bracket.py not read; the ledger-reservation authority chain is verified only at its consumption predicate.
> - joulewise/identity_pins.py internals not line-read; verified via CLI probe + 42-test suite.
> - Full freeze-receipt semantic replay (`_load_freeze_reference` end-to-end) and dry-run generation not executable here: model bytes absent and evidence is boot/monotonic-bound to the production machine → ED-QUAL-L1-1.
> - The `updated`-field truth check is manual; no automated staleness detector was built.

Governing ruling (`council-verdict.md` §VERDICT, VERBATIM):
> **The work-order program is NOT CERTIFIED COMPLETE** (Opus B4 cure, cold §E concurring): every seat's evidence universe was self-nominated, and the one denominator adversarially tested fell. Closing all listed work orders does not entitle READY; the READY-candidate re-audit must re-enumerate every universe independently and run the adversarial coverage attack as a standing packet element.

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND on independent re-enumeration.** `ls docs/process_traces/` shows no
  coverage-re-enumeration artifact for L1 (post-council traces: `2026-08-15-l2-reaudit`, eight
  consult dirs, `2026-08-15-m2-coldgate`, `2026-08-15-recorder-race-coldgate`,
  `2026-08-16-grant-identity-consult`, `2026-08-16-launch-f3-coldgate`,
  `2026-08-16-phase2-plan-consult`, `2026-08-17-freeze-numbering-consult`,
  `2026-08-18-anchor-v3-science-review`, `2026-08-18-freeze-semantics-coldgate`,
  `2026-08-18-shakedown-first-light`, `2026-08-18-t10-t11-working-notes`,
  `2026-08-19-r1-r2-codesign`, `2026-08-19-refreeze-execution`). The only re-audit executed is
  L2's (`0f886d3`, WO-L2-REAUDIT).
- The L1 universe has also **grown** since the audit: `joulewise/arm_readiness.py` gained the R1
  lifecycle block (`:676-711`, `:3299-3403`); the `_v2` and `_v3` pack families (six packs, each
  with generator, plan tree, 33 evidence receipts, freeze receipts, projection receipts) did not
  exist in the audited universe at all; `docs/process/window-run-cards/`,
  `docs/process/d149-go-receipt-template.md`, `docs/process/rehearsal-operator-card.md`,
  `docs/process/ed-*.md` are new authority-plane surfaces.
- **Phase 3 baseline supersession has not happened:** `docs/process/audit-baseline-manifest.json`
  still pins `head_commit ac3fe1d2…`, `origin_main ac3fe1d2…`, the `_v1` pack digests, and lacks
  the ruled `pack_digest_algorithm` field (council ruling: "Manifest conditions at supersession",
  cold §B.2 / Opus S11). Last touched by `694442c`.

### (c) Candidate disposition for the seat
**STILL-OPEN.** The seat is adjudicating a coverage denominator that (i) was never independently
re-enumerated as the verdict ordered, (ii) has grown by an entire successor pack family and a new
lifecycle subsystem since it was counted, and (iii) is measured against a baseline manifest that no
longer describes the operative artifacts.

### (d) Skeptical probes
1. Re-enumerate L1's universe at the sitting head, independently, and compare the denominator to 24. Count the `_v2`/`_v3` families, the R1 lifecycle code, and the new operator-facing authority documents.
2. `git diff --stat ac3fe1d..HEAD -- joulewise/arm_readiness.py configs/arm_readiness/ docs/process/state_kernel.json scripts/gen_state.py` — how much of the audited universe's bytes changed after the audit?
3. Did ED-QUAL-L1-1 (same-boot production replay of the freeze chain per pack + `project_identity_pins.py verify` with real model bytes) execute? Charter amendments 11-12 bind ED-QUALIFICATION rows closed at a READY-candidate sitting.
4. Did ED-QUAL-L1-2 (re-author on the production machine once ruled) execute — and if the `_v3` mint at `/Users/edr/JouleWise-measurement-20260818` IS that execution, where is its custodied evidence and who verified it live?
5. Is there a supersession baseline manifest? If not, against what immutable reference is this row being graded?

---

## ROW-LEVEL OPEN ITEMS
- **L1-S1 (D-118 mechanical gate-ledger enforcement): NO REPAIR.** No checker in `.github/` or `scripts/`; `grep -rn "D-118" scripts .github joulewise tests` returns zero hits; the D-118 index row (`docs/decision_log.md:143`) still asserts "MECHANICALLY CHECKED". Neither WO-L1-4 branch (build the lint / amend the clause) executed.
- **L1-S3 (FREEZE-FCM01.md supersession banner): NO REPAIR.** File unchanged since `60d9e42` (2026-08-11, pre-council). WO-L1-5 not executed. Only the kernel row was deleted.
- **L1-N2 (gen_state invariant 8 substring binding): NO REPAIR**, and its comment now cites the retired P2-006 row.
- **L1-S2 mechanism: NO REPAIR.** No staleness invariant; `gen_state.py` validates date FORMAT and pointer-file EXISTENCE only. Current values are correct by hand and live **branch-only**.
- **L1-B1 recurrence is unaddressed.** The min-inheritance of EXECUTION_BOUND horizons into the arm receipt (`arm_readiness.py:6230-6242`) is unchanged; R1 clause 1 retains the horizon; R1 clause 5 forbids revalidation. The `_v3` family's 33 receipts had **14.85 h** left at 2026-08-20T02:00:47Z. No documented lane exists for what happens when they lapse (D-131 would require another successor family).
- **The operative pack family is not on `main`.** `_v3` packs, freeze-0003 receipts, the D-149 kernel fences, the S6 kernel truth pass, and `ed-s5-mint-decision-2026-08-19.md` are all branch-only on `impl/r2-s0-mint-resolver`. `main` = `0099382` carries `_v1`/`_v2` only.
- **No independent coverage re-enumeration for L1** exists, though `council-verdict.md` makes it a standing packet element for the READY-candidate sitting.
- **No Phase-3 baseline-manifest supersession exists.** `audit-baseline-manifest.json` still pins `ac3fe1d2…` and the `_v1` digests, and lacks the ruled `pack_digest_algorithm` field.
- **Both L1 ED-QUALIFICATION rows (ED-QUAL-L1-1, ED-QUAL-L1-2) have no closure evidence I could locate** in `docs/process_traces/`, `docs/process/ed-*.md`, or `TASK_QUEUE.md`. Searched those three surfaces plus `RUN_STATE.md` by grep for `ED-QUAL-L1`.
- **New, previously unrecorded:** `D117-W-ALPHA`'s kernel `goal` names pack `d117_floor_qwen25_1p5b_v1` while its `acceptance.evidence` names `_v3` — a kernel-truth divergence of exactly the B3/S2 class, introduced after the reconciliation transaction.
- **Assembly-head drift:** this row was verified at `b92b43d`, not the brief's `d10881b`; the branch moved twice during assembly. Any sha the seat re-checks should be re-pinned to the sitting head.
