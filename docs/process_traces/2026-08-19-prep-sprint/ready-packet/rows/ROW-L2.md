# ROW L2 — CALIBRATION ACQUISITION (gating seat, xhigh)

> **Assembler note (read first).** This row is MECHANICALLY ASSEMBLED. No item below is
> graded READY. Where a repair could not be located, the row says so and names what was
> searched.

## HEAD DISCREPANCY — recorded before anything else (material under amendment 12)

Three different "current heads" were given to / found by this assembler. The seat must
rule on which head the packet is about, because charter amendment 12 (`docs/process/
instrument-readiness-audit-charter.md`, §"Verdict form (amendments 11-12)") states:
*"final-head invalidation — any repo change after the baseline manifest voids affected
lens results."*

| Source | Head asserted | Verified? |
|---|---|---|
| This assembler's task brief | `4597ad4` | `4597ad4` exists: "Preserve prep item 3 (D-144 seat-pass packet) into custody before pause" |
| `ready-packet/_ASSEMBLER-BRIEF.md:12` | `d10881b` | not the tip of `impl/r2-s0-mint-resolver` at read time |
| `ready-packet/raw/CHANGE-UNIVERSE-BRIEF.md:4` | `4597ad4`, 214 commits from baseline | `git rev-list --count 8937dec..4597ad4` = **214** ✓ |
| **ACTUAL `wtS0` tip at assembly time** | **`b92b43d`** "Shakedown-v3 first-light run card (prep item 6b): turnkey window lane — GO receipt, in-band check against the r6 band, D-078 refusal handling" | `git log --oneline -1` in `wtS0`; `4597ad4` is its **parent** |

`4597ad4` is checked out detached in the sibling worktree `wtCANON`. The branch advanced
by one commit after the change-universe brief was written. **The seat is being asked to
adjudicate a moving head.** All findings below were verified at the `wtS0` tip
(`b92b43d`) unless a specific SHA is named; where the distinction could matter it is
called out.

**THE HEAD MOVED AGAIN DURING ASSEMBLY OF THIS ROW.** `wtS0` opened at `b92b43d` and
closed at **`7305e0d`** — "Prep sprint: paper staging landed — registry audit (0/34 clean
locators; 8-slot coverage hole; era-codes renderer gap F1), refreshed-registry DRAFT
(anchors only), 5 STOP_FILL figure skeletons + drift-proof generator". `git rev-list
--count 4597ad4..HEAD` = **2** (`b92b43d`, then `7305e0d`); `b92b43d` is an ancestor of the
new tip, so nothing below was invalidated by rewrite — but the branch gained commits *while
the packet was being mechanically assembled*. The worktree itself was never written by this
assembler (`git status --porcelain` empty at close). **A charter-amendment-12 sitting cannot
be held against a branch that is still moving; the seat should require a frozen, named head
before ruling.**

## 0. Seat identity and 2026-08-15 result

**Two distinct recorded verdicts, per charter amendment 11.**

1. **NOT-READY** — `council-verdict.md:12`: "**NOT-READY. 0 READY / 11 NOT-READY** (ten
   gating seats + the non-gating L11 basis seat)."
2. **UNVERIFIED on coverage** — `council-verdict.md:13-16`: "**L2 additionally carries
   UNVERIFIED on coverage** (its denominator was refuted; charter amendment 11 treats the
   verdicts as distinct — the NOT-READY carries the work orders, the UNVERIFIED carries
   the mandatory re-audit)."

**The seat self-reported READY.** `raw/L2-triage.md:6` (extracted from
`docs/process_traces/2026-08-15-readiness-council/triage.json`, seat entry
`L2-CALIBRATION-ACQUISITION`): "seat verdict as reported: **READY**", "coverage: 15/16
(evidence_universe_count=16)". The seat report closes with the single word "READY"
(`seat-reports/L2-CALIBRATION-ACQUISITION-report.md:70-72`).

**This is precisely the falsely-clean case the council flagged.** The adversarial
coverage attack (`refuter-outputs/refuter-L2-out.md`, summarised at
`refuter-outputs/refuter-verdicts.md:17-36`) returned: "READY DOES NOT SURVIVE. L2 ->
NOT-READY", raising the seat's own should-fix L2-1 to blocker and adding
**L2-COV-1**: "coverage 15/16 REFUTED — self-selected universe; omitted contracts,
bootstrap/backfill scripts, 23-test three-window lifecycle module; crash matrix is 13
tests not 16; real direct test universe 251."

The verdict generalises the lesson to the whole program (`council-verdict.md:18-22`):
"**The work-order program is NOT CERTIFIED COMPLETE** … every seat's evidence universe
was self-nominated, and the one denominator adversarially tested fell. Closing all listed
work orders does not entitle READY; the READY-candidate re-audit must re-enumerate every
universe independently and run the adversarial coverage attack as a standing packet
element."

**Single-lens labels and their clearance.** `council-verdict.md:46-49` (Disposition 5)
recorded **L2-1, L2-COV-1, L2-EDQ-1** as SINGLE-LENS with a second distinct-lens refuter
ORDERED before their work orders implement. The ADDENDUM (`council-verdict.md:121-131`)
records that the ordered second lens
(`refuter-outputs/sol-refuter-singlelens.md`, Sol xhigh, execution lens) **confirmed all
four single-lens claims** — "L2-1 (refined: the unbudgeted projection tree is finite but
intractably large — the operational lease-held blocker stands verbatim), L2-COV-1
(251-test universe re-enumerated exactly), L2-EDQ-1 (three 600-s loaded-host failures
durably recorded; qualification open)" — and that "Disposition 5's condition is
discharged."

---

## 1. FINDINGS — original text verbatim, with citation

Finding IDs are `L2-1`…`L2-4` (the seat report and work orders use these; the triage
extract lists them positionally as F1–F4).

### L2-1 — severity at seat: `should_fix`; **RAISED TO BLOCKER by the refuter**

**Title (verbatim, `raw/L2-triage.md:12`):**
> detect_pulses region projection has no work budget — non-termination on degenerate traces while holding the writer lease

**`file_line` (verbatim, `raw/L2-triage.md:13`):**
> `joulewise/powermetrics_fiducial.py:554 (_accepted_region_projection; FIT_HALF_RANGE_S=0.75 at :70, REGION_COVERAGE_RESOLUTION_S=0.0001 at :73); reached from scripts/validate_powermetrics_fiducial.py:1509`

**`failure_scenario` (verbatim, `raw/L2-triage.md:14`):**
> "Quiet-window pre-calibration hits clock_anchor_unresolved (a recorded real production condition — runbook SS10/SS13.1) and the capture's loss surface is flat enough that the 1.5 s x 1.5 s rectangle bisected to 0.1 ms cells (~2.25e8 cells/pulse x 59 pulses) never prunes: the writer computes for hours holding the writer lease, the chain has no watchdog, the operator is forbidden to touch the machine (SS5C), and the funded window burns with no governed exit ever emitted; a consumed one-launch arm capability is lost with it. Witnessed 3x >600 s on this host with the repo's own crash-matrix fixture (SIGABRT stack captured inside _pulse_loss_cell_lower_bound) while a near-identical run finished in 10.7 s — unbounded, data-dependent cost on a refusal path. Consumption soundness is NOT affected (evidence already forced invalid; SIGKILL leaves a fail-closed pending/claimed state — proven by passing witness tests). Also blocks tests.test_calibration_writer_crash_matrix from completing on this audit host (its 600 s subprocess ceiling aborts)."

**Citations:** `raw/L2-triage.md:12-14`; seat report
`seat-reports/L2-CALIBRATION-ACQUISITION-report.md:49` (and executed witness N3 at :44);
refuter escalation `refuter-outputs/refuter-verdicts.md:20-23` ("NEW BLOCKER L2-1 (raised
from L2's own should-fix): detect_pulses region projection has NO finite work budget;
frozen chain calls it synchronously UNDER THE WRITER LEASE"); second-lens clearance
`council-verdict.md:124-126`.

**Work order (verbatim, `raw/L2-triage.md:30`):**
> WO-L2-1 (for L2-1): add a rigorous work budget to _accepted_region_projection (cell-count or wall bound); on exhaustion fail closed with a new detection reason (e.g. detection_nonconvergent -> status invalid, never a bound), and/or skip full-resolution projection entirely when clock anchor is unresolved (the artifact is already forced invalid — full-resolution region evidence buys nothing). Regression: replay the degenerate crash-matrix trace; the crash-matrix module then completes on any host.

---

### L2-2 — severity `should_fix`

**Title (verbatim, `raw/L2-triage.md:16`):**
> readiness/session-status crash with an unregistered raw traceback when the ledger parent directory is missing

**`file_line` (verbatim, `raw/L2-triage.md:17`):**
> `joulewise/calibration_ledger.py:2885 (resolve_ledger_lease_identity parent .resolve(strict=True)) via writer_lease_is_live, uncaught in scripts/recover_calibration_ledger.py:412/:321 (only CalibrationLedgerError is caught)`

**`failure_scenario` (verbatim, `raw/L2-triage.md:18`):**
> "Operator runs the SS5-amendment E-8 readiness command (or session-status) with $CALIBRATION_LEDGER mis-pointed at a path whose parent does not exist (typo, unmounted volume, fresh clone before any ledger exists): FileNotFoundError traceback, exit 1, no registered refusal code, no SS10 row — an unmapped failure that ends the night by SS5C rule 4 instead of a correctable governed refusal. Executed witness: E-8 before E-9 in a fresh scratch checkout crashes exactly this way, while E-9 then succeeds because the lease mkdirs the parent. Bounded: the frozen plan pins CALIBRATION_LEDGER to /Users/edr/code/JouleWise/runs/... which exists, so the documented night is unaffected; inspect handles the same state cleanly (genesis inspection)."

**Citations:** `raw/L2-triage.md:16-18`; seat report :51 and executed witness N4 at :45;
refuter `refuter-outputs/refuter-verdicts.md:29` ("L2-2 missing-parent raw traceback
CONFIRMED should-fix (typed refusal remedy)"); **re-confirmed post-council** as
re-audit finding **L2R-2** (`docs/process_traces/2026-08-15-l2-reaudit/reaudit-report.md`
verdict block id `L2R-2`, and §"L2R-2 — should_fix" at :234-246, with executed probe V7
at :146-159).

**Work order (verbatim, `raw/L2-triage.md:32`):**
> WO-L2-2 (for L2-2): wrap the readiness/session-status/validate-slot dispatch in recover_calibration_ledger.py (and/or resolve_ledger_lease_identity) to convert missing-parent OSError into the registered physical_ledger_unreadable/unsafe_lock_inode refusal envelope so every diagnostic surface fails closed with a SS10 row.

---

### L2-3 — severity at seat: `nit`; **RAISED to should_fix by the refuter**

**Title (verbatim, `raw/L2-triage.md:20`):**
> Runbook needs_pin_commit bullet is unscoped vs the by-design PHYSICAL_AHEAD pre-slot relation

**`file_line` (verbatim, `raw/L2-triage.md:21`):**
> `docs/phase_2/window_runbook.md:421-423 vs joulewise/calibration_ledger.py:4949`

**`failure_scenario` (verbatim, `raw/L2-triage.md:22`):**
> "SS5 amendment says 'Treat needs_pin_commit: true as desk work that ends a 2 a.m. attempt', but the pre-slot readiness (diagnostic and enforcing) reports needs_pin_commit=true whenever ready, because PHYSICAL_AHEAD is the REQUIRED mid-bracket relation (pin deliberately stays at the pre-reservation head until post finalization). A tired operator reading the bullet mechanically at pre-slot aborts every legitimate resume. The adjacent bullet (phase-appropriate pin relation) is correct; the needs_pin_commit bullet should be scoped to pre-reserve/terminal."

**Citations:** `raw/L2-triage.md:20-22`; seat report :53; **severity raised** at
`refuter-outputs/refuter-verdicts.md:30-31`: "L2-3 needs_pin_commit contradiction
CONFIRMED, RAISED nit->should-fix (can mechanically abort every correct pre-slot
session)."

**Work order (verbatim, `raw/L2-triage.md:34`):**
> WO-L2-3 (nit): scope the runbook SS5-amendment needs_pin_commit bullet to pre-reserve/terminal phases (pre-slot's ready state is physical_ahead by design).

---

### L2-4 — **STRUCK: PHANTOM**

**Title (verbatim, `raw/L2-triage.md:24`):**
> Idempotent re-reservation returns status:reserved without re-printing calibration_pre_reserve_authorized

**`file_line` (verbatim, `raw/L2-triage.md:25`):**
> `scripts/reserve_calibration_window_bracket.py:172-201 (event printed only on ready readiness; fall-through resume path appends idempotently)`

**`failure_scenario` (verbatim, `raw/L2-triage.md:26`):**
> "SS5C requires both the authorized event and status:reserved; after an accidental double-run of E-9 the second invocation (readiness blocked by the now-open session, session-status found, idempotent completed-op return) prints status:reserved with no authorized event — an operator matching the runbook's required markers sees a discrepancy on a harmless governed resume. Executed: rerun was byte-identical, exit 0. Runbook already forbids re-reservation on restart; document the resume output shape."

**STRUCK — verbatim disposition, `council-verdict.md:44-45` (Disposition 4):**
> **Struck findings:** L8-B4 (both lenses: wrong-path artifact; correct fail-closed refusal), WO-L2-4 (phantom), F4's timing premise (privilege gap survives inside WO-T0-PRODUCER).

Refuter basis, verbatim `refuter-outputs/refuter-verdicts.md:32`:
> L2-4 idempotent-marker WO REFUTED as phantom (runbook forbids re-reserving; reprint would mislead) — drop WO-L2-4.

Also carried in the adjudication tally, `refuter-verdicts.md:125`: "DEAD: … WO-L2-4
(phantom)". **No repair is owed and none should be attached.** The struck work-order text
(`raw/L2-triage.md:36`) is preserved for the record: "WO-L2-4 (nit): document the
reservation CLI's idempotent-resume output shape (status:reserved without a re-printed
authorized event) in SS6."

---

### L2-COV-1 — the coverage denominator (the UNVERIFIED verdict's subject)

Not a seat finding; **raised by the falsely-clean refuter**. Verbatim,
`refuter-outputs/refuter-verdicts.md:24-26`:
> NEW BLOCKER L2-COV-1: coverage 15/16 REFUTED — self-selected universe; omitted contracts, bootstrap/backfill scripts, 23-test three-window lifecycle module; crash matrix is 13 tests not 16; real direct test universe 251.

Confirmed by the second lens (`council-verdict.md:126`): "L2-COV-1 (251-test universe
re-enumerated exactly)".

### L2-EDQ-1 — deferred ED-QUAL at READY

Verbatim, `refuter-outputs/refuter-verdicts.md:27-28`:
> NEW BLOCKER L2-EDQ-1: charter forbids deferred ED-QUAL at READY; live writer/sudo + crash-matrix qualification open.

Council-recorded state after second lens (`council-verdict.md:126-127`): "L2-EDQ-1 (three
600-s loaded-host failures durably recorded; **qualification open**)".

---

## 2. WHAT CHANGED SINCE 2026-08-15

### 2.a THE MANDATORY RE-AUDIT — WO-L2-REAUDIT (discharges the UNVERIFIED verdict)

- **Custody:** `docs/process_traces/2026-08-15-l2-reaudit/` — `README.md`,
  `reaudit-prompt.md`, `reaudit-report.md`. Custody commit **`0f886d3`** ("Custody dir
  local-date correction (08-16 → 08-15; audit completed 23:29 PDT 08-15)") — verified by
  `git log --oneline -1 0f886d3`.
- **TASK_QUEUE line 103** (verified by grep, Completed Queue Items table): row
  `WO-L2-REAUDIT | P1 Phase Gate | 2026-08-15`, evidence text: "DELIVERED same-day:
  Coverage VERIFIED — 251/251 test IDs independently enumerated (procedure
  sensitivity-probed ×3), 247/251 current-head executed (242 pass, 5 declared skips, 4
  crash-matrix IDs attributed to the registered WO-DETECT-PULSES-BUDGET limitation); L2R-2
  folded into the L2-2 batch. Custody `docs/process_traces/2026-08-15-l2-reaudit/`
  (0f886d3)."
- **WHERE it lives:** merged to main; `0f886d3` is an ancestor of `origin/main`
  (`0099382`) and of the branch head.

**What the re-audit actually enumerated (from `reaudit-report.md`):**

| Quantity | Value | Where |
|---|---|---|
| Test IDs independently enumerated | **251 / 251** | verdict block `enumeration: {numerator: 251, denominator: 251}`; §"Coverage accounting" :284 |
| Current-head execution | **247 / 251** | verdict `current_head_execution` |
| Passing test bodies | **242** | `passed_test_bodies: 242` |
| Declared skips | **5** | `skipped: 5` (two D-079 import-fixture skips; three "U2 successor engine pending", :287-291) |
| Unexecuted | **4** crash-matrix IDs | `unexecuted: 4`; named at :225-228 |
| Non-test universe | 26 enumerated, **25 present**, 1 external runtime artifact absent | `non_test_evidence`; :271-278 |
| Denominator sensitivity probes | **3** (P1/P2/P3, each 251→250) | :296-303 |
| Adversarial coverage attack | executed, 9 failure classes tabled | :306-318 |

Per-module table (`reaudit-report.md:259-269`): `test_authentication_io` 18 ·
`test_calibration_bracketing` 42 · `test_calibration_custody_store` 7 ·
`test_calibration_exits` 30 · `test_calibration_ledger` 72 ·
`test_calibration_live_three_window` 23 · `test_powermetrics_fiducial` 46 ·
`test_calibration_writer_crash_matrix` 13 — **total 251**.

Verdict text verbatim (`reaudit-report.md:322-324`):
> **Coverage VERIFIED: 251/251 independently enumerated and dispositioned.**
> This closes the distinct uncertainty about L2's coverage denominator. It does not claim 251/251 current-head execution, does not certify the remediation branch, and does not alter the council's separate **NOT-READY** machine verdict.

**AT WHICH HEAD — the decisive fact under amendment 12.**

The re-audit ran at **`fac87d1`** — verified three ways: the report's `workspace` block
(`head_start` / `head_end` / `upstream_end` all
`fac87d1f8350ab5277d45f422fbfa6098630efe4`); its own verification probe V9
(`reaudit-report.md:176-189`) recording HEAD == origin/main == `fac87d1…`; and the custody
README (`docs/process_traces/2026-08-15-l2-reaudit/README.md:11`): "`reaudit-report.md` —
Sol xhigh report, executed at main head `fac87d1`."

`fac87d1` = "T8 session record + C-058 addendum: run report (dictated-fills,
mechanic-verified, 26-commit span)…".

**`fac87d1` is NOT the current head. It is an ancestor, and it is stale by 187 commits.**
Mechanically verified in `wtS0`:

```
git merge-base --is-ancestor fac87d1 4597ad4   → true
git rev-list --count fac87d1..4597ad4          → 187
git rev-list --count 8937dec..4597ad4          → 214   (matches CHANGE-UNIVERSE-BRIEF:5)
git merge-base --is-ancestor fac87d1 origin/main → true
```

The `wtS0` tip is `b92b43d`, one commit beyond `4597ad4` — so **188** commits separate the
re-audit head from the actual tip. Amendment 12's final-head invalidation
(`instrument-readiness-audit-charter.md`, §"Verdict form (amendments 11-12)") applies on
its face; the seat must rule whether the coverage verification survives it.

**The denominator has demonstrably moved.** Mechanical count of `    def test_` across
exactly the eight modules the re-audit enumerated (this counting method reproduces the
re-audit's loader total **exactly** at `fac87d1`, which is why it is trustworthy as a
delta indicator — it is NOT a `countTestCases()` substitute):

| Module | @ `fac87d1` | @ `wtS0` tip | Δ |
|---|---:|---:|---:|
| `test_authentication_io` | 18 | 18 | — |
| `test_calibration_bracketing` | 42 | 48 | **+6** |
| `test_calibration_custody_store` | 7 | 7 | — |
| `test_calibration_exits` | 30 | 31 | **+1** |
| `test_calibration_ledger` | 72 | 72 | — |
| `test_calibration_live_three_window` | 23 | 23 | — |
| `test_powermetrics_fiducial` | 46 | 75 | **+29** |
| `test_calibration_writer_crash_matrix` | 13 | 15 | **+2** |
| **TOTAL** | **251** ✓ | **289** | **+38 (+15.1%)** |

The re-audit's own §"Verdict" claims 251/251 as a *closed* universe. At the current head
that universe is 289 by the same procedure — and the re-audit's enumeration procedure
(:250-257) would additionally have to be re-run to decide whether any *new module* now
belongs in the L2 denominator. **Nothing in the packet re-runs it at the current head.**

### 2.b L2-1 — WO-DETECT-PULSES-BUDGET: cure LANDED, work-order row STILL OPEN

- **Implementing commit:** `ceda7a6` "WO-DETECT-PULSES-BUDGET: deterministic projection
  budget + anchor-unresolved bypass + governed nonconvergent abort" (found via
  `git log -S"DETECTION_PROJECTION_CELL_BUDGET" -- joulewise/powermetrics_fiducial.py`).
- **WHERE it lives: merged to main AND on the branch.** `git show
  origin/main:joulewise/powermetrics_fiducial.py` contains
  `DETECTION_PROJECTION_CELL_BUDGET = 165_000` (:87) and
  `DETECTION_PROJECTION_WALL_BUDGET_S = 120.0` (:91). Branch tip carries the identical
  values at :88 / :92.
- **Code at current head** (`joulewise/powermetrics_fiducial.py`): `DETECTION_NONCONVERGENT
  = "detection_nonconvergent"` (:93) — the exact registered reason WO-L2-1 specified;
  `_ProjectionWorkBudget` dataclass (:526-547) enforcing "One shared budget across every
  pulse in a detection attempt" with `trigger="evaluated_cell_budget"` and a wall-clock
  arm; threaded through `_accepted_region_projection` via `work_budget.consume_cell()`
  (:668) and `projection_work_budget` (:743, :870).
- **The budget value CHANGED after the work order** — this is a separate ruling, not the
  WO: **D-143** (`docs/decision_log.md:166`) "DETECTION-PROJECTION CELL BUDGET 100,000 →
  165,000 (magistrate parameter ruling, 2026-08-18; license records:
  `docs/process_traces/2026-08-18-shakedown-first-light/` 02+03): the maiden live capture
  and three issued corpus members all exhaust 100k under the budgeted detector (real
  workload 112,205–137,189 cells, n=34 complete-corpus sweep); 165,000 = max + 20.3%
  headroom, exceeding the whole observed spread; fail-closed semantics retained;
  behavioural kill tests pin the production path." Note the ruling records that the
  **as-shipped 100k budget would have fired on real production workloads** — the first
  parameter choice was wrong against live data.
- **D-138** (`docs/decision_log.md:163`) governs how it landed: "any change to the four
  governed estimator inputs (`joulewise/powermetrics_fiducial.py`, `uncertainty_evidence.py`,
  `adapters/powermetrics.py`, `reduce.py`) stages on the Phase-2 transaction branch and
  lands only inside the ONE atomic successor-family re-freeze that folds the D-079
  acceptance re-issue."
- **TASK_QUEUE A5 row is STILL OPEN.** Generated Current Queue: `| A5 |
  WO-DETECT-PULSES-BUDGET | P1 Phase Gate | **PARTIAL; READY [AGENT]** | …` Note text:
  "COMPLETE Phase-2 payload on impl/wo-detect-pulses-budget @ e22e658 (main-synced):
  detection budget + calexits flake fix + calibration-side launch-lineage stage 2 — each
  delta-ACCEPTED (final: 9/9 settle, 81/81 focused). MERGE-STAGED for the atomic re-freeze
  (D-138); plan custodied docs/process_traces/2026-08-16-phase2-plan-consult/". A second
  generated occurrence appears later in the file as `| A5 | … | PARTIAL; READY | …`.
- **Hand-authored evidence note, `TASK_QUEUE.md:317-336`** (verbatim excerpts): "On-host
  the formerly blocked crash matrix completed all 14 tests in 98.964 seconds with no
  internal timeout." / "This hand-authored evidence note **does not retire the generated
  A5 row**: kernel/checklist closure and the later D-079 acceptance/pin re-freeze remain
  lead-owned." / "Canonical replay reached all 3,293 tests in 1,122.980 seconds with no
  timeout; its 37 failures and one error are the expected authenticated-estimator pin
  fan-out … until that re-freeze, not a license to weaken or locally rewrite frozen
  production pins."
  Note the note still describes the **100,000**-cell budget ("adds the frozen 100,000-cell
  whole-detection budget") — stale against D-143's 165,000.
- The re-audit at `fac87d1` explicitly **refused to count** this branch evidence
  (`reaudit-report.md` flag F3: "The 14-OK/99s evidence belongs to ceda7a6 on
  impl/wo-detect-pulses-budget, not fac87d1; remediation was not graded."). At the current
  head that objection no longer applies — the code is on main.

### 2.c L2-2 — **NO REPAIR FOUND at the current head**

Verified in `wtS0` at the tip:

- `joulewise/calibration_ledger.py:2885` still reads
  `canonical_parent = canonical_path.parent.resolve(strict=True)` — the **exact cited
  line, unchanged**.
- `scripts/recover_calibration_ledger.py` has exactly **one** top-level handler:
  `except CalibrationLedgerError as exc:` at **:484**. No `except OSError`, no
  `except Exception`, no missing-parent conversion. (`grep -n "except CalibrationLedgerError\|except OSError\|except Exception"` returns that single line.)
- The re-audit reproduced the defect at `fac87d1` (probe V7, `reaudit-report.md:146-159`:
  `FileNotFoundError: [Errno 2] No such file or directory`, exit 1) and recorded
  `L2R-2`: "The exact missing-parent route is uncovered and still fails outside the
  refusal registry… No enumerated test constructs this exact absent-parent diagnostic
  route." Disposition: "the council's existing L2-2 should-fix batch. This is not a new
  work order."
- **Searched for a repair:** `grep` for `physical_ledger_unreadable`,
  `unsafe_lock_inode`, `FileNotFoundError`, `OSError` in
  `scripts/recover_calibration_ledger.py`; `grep -n "strict=True"` in
  `joulewise/calibration_ledger.py`; `grep` for `WO-L2-2` / "should-fix batch" in
  `TASK_QUEUE.md`. **No WO-L2-2 row, no completed-queue entry, and no code change
  located.** The council's "should-fix batch incl. sweep verify-and-fix items"
  (`council-verdict.md:85-87`) is the only place it is programmatically owed.

### 2.d L2-3 — **NO REPAIR FOUND at the current head**

The runbook bullet is **byte-identical to the audit baseline**. Verified by diffing the
region:

- `git show 8937dec:docs/phase_2/window_runbook.md | sed -n '419,425p'` →
  "- [ ] Treat `needs_pin_commit: true` as desk work that ends a 2 a.m. attempt. / It never
  licenses an uncommitted-pin override."
- Current head `docs/phase_2/window_runbook.md:453-454` → the **same two lines**, now at a
  shifted line number (the file grew). No pre-reserve/terminal scoping was added.

**Searched:** `grep -n "needs_pin_commit" docs/phase_2/window_runbook.md` (hits at :453,
:991, :1100, :1573 — none of which scopes the §5-amendment bullet to
pre-reserve/terminal); `grep` for `WO-L2-3` in `TASK_QUEUE.md` (no row). Note the refuter
raised this to should_fix (`refuter-verdicts.md:30-31`), so it is not a nit the seat may
wave through on severity grounds.

### 2.e L2-4 — struck; nothing owed

See §1. Recorded as PHANTOM at `council-verdict.md:44-45` and `refuter-verdicts.md:32,125`.

### 2.f Context the seat needs about the tree the L2 surfaces now sit in

These did not repair an L2 finding but changed the code and artifacts L2 governs, and
therefore bear on whether any 2026-08-15 or `fac87d1` result transfers:

- **D-146** (`docs/decision_log.md:169`) — R1 ruling, production capture-pipeline v3:
  "p2-038.3 schema+method identity with single-key dispatch and
  `clock_anchor_era_inconsistent` cross-check; eras retained forever; era-faithful strict
  verify …; ONE shared claim-barrier predicate (`CLAIM_BEARING_ANCHOR_METHODS`) with NEW
  engine reason `capture_pipeline_superseded`". Landed in **`b7e5730`** "S1: anchor-v3
  production flip + D-079 r5 (science-neutral, 19-member replay proven) + claim barrier
  (D-146)". Branch-only (not on `origin/main` = `0099382`).
- **D-147** (`docs/decision_log.md:170`) — R2 mint-lane ruling; the S0–S5 commit chain on
  the branch: `cef3306` (S0 kernel), `6771924`, `8018a4b` (S0 fix round 1), `b7e5730` (S1),
  `1ec5dc4`, `3038eeb` (S1 fix round 2 — forced the r6 reissue), `d279bd2`, `6f00d05`,
  `d8f1202` (S2 goldens), `1d3873b` (S3 `_v3` family), `8b2b021` (S5 confirmation table).
- **r6 supersedes r5** — `docs/process_traces/2026-08-19-r1-r2-codesign/15-amendment-r6.md`:
  "S1 fix round 2 (commit 3038eeb) … edited `joulewise/uncertainty_evidence.py` and
  `joulewise/reduce.py` — two of the four D-079-pinned estimator sources — and therefore
  forced the science-neutral r6 reissue in the same commit (19-member replay, zero
  mismatches …)". Both `configs/calibration/calibration_acceptance_d079_v2_n17_r5.json`
  and `…_n17_r6.json` exist at the current head; `joulewise/calibration_bracketing.py` and
  `joulewise/arm_readiness.py` each reference **both** generations.
- `joulewise/powermetrics_fiducial.py` — the file carrying L2-1's cure — is one of the four
  **D-079-pinned estimator sources** (D-138), so every L2 detector change is coupled to the
  acceptance-artifact generation the seat's own E9/E11 evidence items pin.

---

## 3. ED-QUALIFICATION ROWS

### EDQ-L2-1 — crash-matrix run to completion on a quiet bench

**Verbatim row text (`raw/L2-triage.md:40`):**
> EDQ-L2-1 (stable capability): execute tests.test_calibration_writer_crash_matrix to completion on the quiet bench at the audit-baseline head and record pass + wall time. On the audited host it cannot complete (finding L2-1); CI exclusive-job green at the baseline head corroborates but a bench execution closes the row with local evidence.

Council-recorded state at the sitting (verdict ADDENDUM, `council-verdict.md:126-127`):
"L2-EDQ-1 (three 600-s loaded-host failures durably recorded; **qualification open**)".

**LOCATED CLOSURE EVIDENCE — partial, with a named mismatch.**

`docs/process_traces/2026-08-18-freeze-semantics-coldgate/verification-logs/crash-matrix-quiet-20260818-0110PT.log`
(3,394 bytes, tracked). Contents: a full unpiped verbose run listing **15** named test
methods each `... ok`, terminating:

```
----------------------------------------------------------------------
Ran 15 tests in 535.763s

OK
```

Two of the fifteen are the L2-1 cure's own regressions —
`test_detection_budget_refuses_with_terminal_custody_and_released_lease` and
`test_post_detection_budget_has_terminal_custody_and_released_lease` — which is why the
module is 15 methods now and 13 at the baseline.

Corroborating narrative, `docs/run_reports/2026-08-18-t10-session.md:249-252`: "The
**crash-matrix module** — which had failed `errors=3` in 1847 s under heavy concurrent
load earlier in the evening — **reran quiet at 15/15 OK**, confirming the load-flake
reading (C-055 precedent) rather than a branch blocker (see Anomalies A-3 for the evidence
gap)."

**Three qualifications the seat must weigh, all from the repo's own record:**

1. **Wrong head.** The row demands execution "at the **audit-baseline head**". The log
   contains **no HEAD line** (verified — the file opens directly on the first test line);
   the run is dated 2026-08-18, i.e. on the Phase-2 transaction branch, ~3 days and
   hundreds of commits past baseline `8937dec`. The 15-method module could not have
   existed at the baseline head, where it had 13.
2. **The evidence was initially recorded as MISSING, then re-custodied.** Anomaly A-3
   verbatim (`docs/run_reports/2026-08-18-t10-session.md:576-587`): "**A-3 — the
   quiet-slot canonical suite and crash-matrix logs are not locatable, and the '13' in the
   load run does not reconcile.** The quiet-slot rule required **full unpiped output to a
   file** for both the canonical suite and the crash-matrix rerun; no such file exists in
   the session scratchpad or any worktree scratch searched by mtime and size. The **15/15
   OK quiet** result is corroborated only by the magistrate's RUN_STATE line at `62c6a06`.
   … The load run's recorded '**errors=3 of 13**' cannot be reconciled with that count —
   and by the trace's own admission that run's output was destroyed by `| tail -3`, so the
   13 is most likely a misread of the masked tail. Treated here as: quiet rerun 15/15, load
   run failed with masked detail."
   Magistrate disposition, same file :545-548: "A-3: the quiet crash-matrix log **is now
   custodied at** `docs/process_traces/2026-08-18-freeze-semantics-coldgate/verification-logs/`;
   the load-run '13 tests' figure is untrusted (tail-masked) and the quiet unpiped 15/15 run
   is authoritative."
3. **The canonical-suite half of the same quiet slot is still not located.** A-3 names two
   missing logs; only the crash-matrix one was re-custodied.

### EDQ-L2-2 — the non-delegable §5C lead live verification

**Verbatim row text (`raw/L2-triage.md:42`):**
> EDQ-L2-2 (stable capability; runbook-mandated non-delegable): the SS5C lead live verification on the exact reviewed measurement checkout — frozen plan's literal readiness-validator command plus the complete under-lease synthetic rehearsal (real reservation CLI --execute + production writer lifecycle through BOTH slots against a synthetic root), requiring the D-134 dry-run receipt PASS/NOT_APPLICABLE with the reviewed HEAD + committed-pack digest. This audit replayed the equivalent in scratch; the runbook requires it on the production checkout with the frozen plan, which no sandboxed seat can perform.

**NO CLOSURE EVIDENCE LOCATED — the row appears explicitly OPEN.**

The nearest artefact is the T10 Ed-qualification table
(`docs/run_reports/2026-08-18-t10-session.md`, custody root
`~/JouleWise-window-custody/ed-qual-20260817/`), whose final row reads verbatim:

> | **Dress rehearsal** | **OPEN** — gated on the frozen `_v2` alpha pack, i.e. on Ed's item-1 ruling | morning packet §4 |

That table closes five *other* Ed rows (D-127 sudoers, sampler lifecycle, rail probe,
backlight, ED-QUAL-L4-1, ED-Q-L9-3) and leaves the rehearsal — the vehicle for EDQ-L2-2's
author→arm→verify→consume leg — open.

**Searched:** `grep -rn "EDQ-L2-2\|§5C live\|SS5C live" docs/ RUN_STATE.md` — the only hits
are the *statements of the obligation* (`council-verdict.md:94`; `triage.json:236`;
`sitting-packet-FINAL.md:182`; the seat report :67) plus one unrelated historical PASS from
2026-08-13 (`docs/run_reports/2026-08-13-t6-session.md:908`, "Three packs frozen; §5C live
verification PASS" — a **pre-council** freeze-execution event, not this row).
`grep -n "rehearsal" RUN_STATE.md` → :458, :543, :622, all of which list the dress
rehearsal as a *pending* Ed-required item ("dress rehearsal E-4→E-9 +
author→arm→verify→consume vs scratch custody"). No receipt, no D-134 dry-run PASS bound to
a reviewed HEAD + committed-pack digest, no custody directory for it was found.

### L2-EDQ-1 (the refuter-raised blocker, distinct from the two seat rows)

Council record (`council-verdict.md:126-127`): "L2-EDQ-1 (three 600-s loaded-host failures
durably recorded; **qualification open**)". The three durably-recorded failures are
itemised in `TASK_QUEUE.md:336-346` (WO-CRASHMATRIX-RELIABILITY section): "a loaded-bench
refuter run hit three internal 600-second per-case ceilings
(test_ambient_writer_crash_stage_is_inert_without_capability,
test_every_exact_stage_pre_and_post_sigkill_reaches_fresh_governed_exit,
test_torn_and_fsynced_append_boundaries_resume_from_fresh_processes; 1,848.071 s module
total, FAILED errors=3)." All three appear as `... ok` in the 2026-08-18 quiet log.
**WO-CRASHMATRIX-RELIABILITY itself remains an open registered row** — no completion entry
found in the Completed Queue table.

---

## 4. CANDIDATE DISPOSITIONS FOR THE SEAT TO ADJUDICATE

**Candidate dispositions are assembled, not adjudicated; the seat rules.**

| Item | Candidate disposition | What is attached / what remains |
|---|---|---|
| **NOT-READY verdict (machine)** | STILL-OPEN | Composite of the rows below. The re-audit states outright it "does not alter the council's separate **NOT-READY** machine verdict" (`reaudit-report.md:324`). |
| **UNVERIFIED-on-coverage verdict** (distinct per amendment 11; carries its own mandatory re-audit) | **STILL-OPEN — evidence attached but head-stale** | WO-L2-REAUDIT delivered a genuine independent enumeration (251/251, 3 sensitivity probes, 9-class adversarial attack) at **`fac87d1`**, custody `0f886d3`, TASK_QUEUE:103. But `fac87d1` is **187 commits behind `4597ad4` / 188 behind the `wtS0` tip**, and the same enumeration procedure yields **289**, not 251, at the current head (+38, +15.1%). Amendment 12's final-head invalidation is squarely engaged, and `council-verdict.md:20-22` makes universe re-enumeration a **standing** packet element, not a one-time discharge. |
| **L2-1** (blocker as raised) | READY-EVIDENCE-ATTACHED — with two open threads | Cure `ceda7a6` is on `origin/main` and the branch: `DETECTION_PROJECTION_CELL_BUDGET = 165_000`, `DETECTION_PROJECTION_WALL_BUDGET_S = 120.0`, `DETECTION_NONCONVERGENT`, `_ProjectionWorkBudget`. Remaining: (a) generated TASK_QUEUE row **A5 is still `PARTIAL; READY [AGENT]`** and the hand-authored note says it "does not retire the generated A5 row"; (b) the shipped budget was re-ruled 100k→165k by **D-143** because real workloads exhausted the first value — a parameter chosen once and already wrong once. |
| **L2-2** (should_fix; re-confirmed post-council as L2R-2) | **STILL-OPEN — NO-REPAIR-FOUND** | `calibration_ledger.py:2885` unchanged (`resolve(strict=True)`); `recover_calibration_ledger.py:484` still the sole handler, `CalibrationLedgerError` only. Remains: implement WO-L2-2's typed-refusal conversion + a test constructing the exact absent-parent diagnostic route (the re-audit found none exists). |
| **L2-3** (raised nit→should_fix) | **STILL-OPEN — NO-REPAIR-FOUND** | Runbook bullet at :453-454 is **byte-identical to baseline `8937dec`**. Remains: scope the §5-amendment bullet to pre-reserve/terminal. |
| **L2-4** | **STRUCK-AT-2026-08-15** | PHANTOM per `council-verdict.md:44-45`; drop per `refuter-verdicts.md:32`. Nothing owed; the seat should confirm no repair was silently attached. |
| **L2-COV-1** | folded into the UNVERIFIED row above | 251 confirmed exactly by the second lens at the sitting; superseded in fact by the head drift. |
| **EDQ-L2-1** | **ED-ROW — closed-with-evidence AT A DIFFERENT HEAD** | `crash-matrix-quiet-20260818-0110PT.log`: Ran 15 tests in 535.763s, OK, full unpiped. But the row specifies the **audit-baseline head**; the log carries **no head pin**; the module was 13 methods at baseline and 15 in the log; and the log was recorded MISSING as anomaly A-3 before being re-custodied. The canonical-suite half of the same quiet slot is still not locatable. |
| **EDQ-L2-2** | **ED-ROW — OPEN** | No closure evidence located. Dress rehearsal explicitly **OPEN** in the T10 Ed-qualification table, gated on the frozen `_v2` alpha pack. Non-delegable by the row's own terms. |
| **L2-EDQ-1** (refuter-raised) | **ED-ROW — OPEN per the council's own words** | "qualification open" (`council-verdict.md:127`). The three 600-s failures now pass in the quiet log, but **WO-CRASHMATRIX-RELIABILITY** has no completion entry. |

---

## 5. WHAT A SKEPTICAL SEAT SHOULD PROBE

All commands assume `cd <wtS0>`; all are read-only.

**P1 (MANDATORY — re-run the adversarial coverage attack at the CURRENT head).**
`council-verdict.md:20-22` makes universe re-enumeration "a standing packet element", not
a discharged obligation. Re-execute `docs/process_traces/2026-08-15-l2-reaudit/reaudit-prompt.md`
verbatim against the current head with a fresh, independent enumerator that is **not shown
the number 251**.
*Falsifier:* if the re-enumeration returns 251, or returns a denominator the enumerator
cannot derive without the prior report, the procedure is reproducing a memorised total
rather than measuring — the exact failure the original P1/P2/P3 sensitivity probes were
built to exclude (`reaudit-report.md:296-304`).

**P2 (MANDATORY — does the 251 denominator still hold after 214 commits?).** Run the
re-audit's own V1:
```
env PYTHONDONTWRITEBYTECODE=1 python3 -c "import unittest; ms=('tests.test_authentication_io','tests.test_calibration_bracketing','tests.test_calibration_custody_store','tests.test_calibration_exits','tests.test_calibration_ledger','tests.test_calibration_live_three_window','tests.test_powermetrics_fiducial','tests.test_calibration_writer_crash_matrix'); print([(m,unittest.defaultTestLoader.loadTestsFromName(m).countTestCases()) for m in ms])"
```
*Expected from this assembler's static count:* ~**289**, not 251 — driven by
`test_powermetrics_fiducial` 46→75 and `test_calibration_bracketing` 42→48.
*Falsifier:* if it returns 251, this assembler's static method count is wrong and the row's
central drift claim collapses. If it returns 289 (or anything ≠ 251), the coverage
verification is arithmetically stale and the UNVERIFIED verdict cannot be discharged by
citing `reaudit-report.md`.

**P3 (the enumeration procedure itself may now be under-inclusive).** The re-audit's
inclusion rule (`reaudit-report.md:252-256`) admits "an entire test module when its primary
contract is one of those L2 surfaces". Since `fac87d1`, the branch added anchor-v3 /
capture-era / mint-lane machinery (`b7e5730`, `1ec5dc4`, `3038eeb`, `1d3873b`) that touches
`joulewise/powermetrics_fiducial.py` and `uncertainty_evidence.py`. Enumerate every test
module added or renamed in `fac87d1..HEAD` and apply the rule to each.
*Falsifier:* any new module whose primary contract is a charter L2 noun (fiducial writer,
authenticated acceptance, bracket reservation, ledger, recovery, writer lifecycle) and
which is absent from the eight-module list means the denominator is under-counted even at
289.

**P4 (L2-2 is claimed unrepaired — verify or refute).**
```
grep -n "except CalibrationLedgerError\|except OSError\|except Exception" scripts/recover_calibration_ledger.py
sed -n '2880,2890p' joulewise/calibration_ledger.py
JW=$(mktemp -d); env PYTHONDONTWRITEBYTECODE=1 python3 scripts/recover_calibration_ledger.py --ledger "$JW/absent/ledger.jsonl" --head-pin configs/calibration/calibration_ledger_head.json readiness --phase terminal
```
*Falsifier:* a registered refusal envelope (`physical_ledger_unreadable` /
`unsafe_lock_inode`) with a §10 row instead of a raw `FileNotFoundError` traceback would
refute this row's NO-REPAIR-FOUND. This assembler reproduced only the static code state,
not the runtime probe — **the seat should execute it.**

**P5 (L2-3 is claimed byte-identical to baseline — verify).**
```
diff <(git show 8937dec:docs/phase_2/window_runbook.md | sed -n '419,425p') <(sed -n '451,457p' docs/phase_2/window_runbook.md)
```
*Falsifier:* any pre-reserve/terminal scoping added anywhere in the runbook (search the
whole file, not just the bullet) refutes NO-REPAIR-FOUND. Note the refuter raised this to
should_fix, so a "documentation nit" framing is not available to the seat without
overturning `refuter-verdicts.md:30-31`.

**P6 (EDQ-L2-1: bind the quiet log to a head, or don't count it).** The log carries no HEAD
line. Determine the head from `git log --format='%H %ci' --before='2026-08-18 01:10' -1
<branch>` and from `62c6a06` (the RUN_STATE commit A-3 names as the sole corroborator), then
ask whether a 15-method module run on the Phase-2 branch discharges a row that says "at the
audit-baseline head" where the module had 13 methods.
*Falsifier:* a head pin inside or alongside the log, or an explicit magistrate amendment
re-scoping the row to the current head, would close the gap. Absent either, the row is
closed against a different artefact than the one it names.

**P7 (the load-vs-quiet reading is a single-observation inference).** A-3 concedes the load
run's output "was destroyed by `| tail -3`" and that 15/15 is "corroborated only by the
magistrate's RUN_STATE line at `62c6a06`". Re-run the module under comparable concurrent
load at the current head.
*Falsifier:* any per-case 600-s ceiling recurring under load means the budget cure fixed the
degenerate-projection path but **not** the CPU-amplifying-fixture class
WO-CRASHMATRIX-RELIABILITY was registered for — two different defects that the "load flake"
reading merges into one.

**P8 (the budget parameter has already been wrong once).** D-143 raised 100k→165k because
"the maiden live capture and three issued corpus members all exhaust 100k … (real workload
112,205–137,189 cells, n=34 complete-corpus sweep)". Ask: what is the *distributional* basis
for 165,000 surviving a workload outside that n=34 sweep, and what happens operationally when
it fires?
*Falsifier:* if budget exhaustion on a real funded window produces `detection_nonconvergent`
→ invalid evidence → governed abort, L2-1's cure holds and the window is merely lost, not
corrupted. If any path can turn exhaustion into partial-valid evidence, the A5 fence ("Do not
turn budget exhaustion into partial-valid evidence or an unregistered operator override") is
breached.

**P9 (A5 is still open — find out what closure requires).** Read the A5 row's Evidence /
Acceptance clauses in `TASK_QUEUE.md` and `docs/process/state_kernel.json`, and reconcile
against the hand-authored note's own disclaimer that it "does not retire the generated A5
row".
*Falsifier:* if kernel acceptance for A5 is already satisfied at the current head, the row is
bookkeeping lag; if it turns on the atomic re-freeze (D-138), L2-1's cure is contingent on a
Phase-2 step that has not completed.

**P10 (the L2 surfaces moved under the seat).** `joulewise/powermetrics_fiducial.py` is one
of the four D-079-pinned estimator sources (D-138). The r5→r6 supersession
(`15-amendment-r6.md`) was forced by a **fix round** editing two of those four files.
*Falsifier:* if any 2026-08-15 L2 probe result (P1's derived screen 0.033558756679900, N1's
exact-byte acceptance refusal, P5's live-ledger seq-76 audit) no longer reproduces at the
current head against the r6 acceptance artefact, those seat results are void under amendment
12 independently of the coverage question.

---

## 6. OPEN ITEMS FROM THIS ROW

- **The packet does not agree with itself about the current head.** Task brief says
  `4597ad4`; `_ASSEMBLER-BRIEF.md:12` says `d10881b`; the actual `wtS0` tip is `b92b43d`
  (parent `4597ad4`). Under amendment 12 the seat cannot adjudicate without a ruled head.
- **The branch gained two commits (`b92b43d`, `7305e0d`) while this packet was being
  assembled.** The head is live. An amendment-12 sitting requires a frozen, named head.
- **The mandatory coverage re-audit ran at `fac87d1`, 187–188 commits behind the current
  head.** Amendment 12's final-head invalidation is engaged and nothing in the packet
  addresses it.
- **The 251 denominator no longer holds.** The same eight modules carry 289 test methods at
  the current head (+38). No re-enumeration at the current head exists.
- **The re-audit's enumeration procedure has not been re-applied** to modules added in
  `fac87d1..HEAD`; a new L2-surface module would enlarge the universe beyond even 289.
- **L2-2: no repair located.** `calibration_ledger.py:2885` and
  `recover_calibration_ledger.py:484` are unchanged; no WO-L2-2 queue row exists; the
  re-audit re-found it as L2R-2 and folded it back into the same unimplemented batch.
  Searched: those two files, `TASK_QUEUE.md`, the Completed Queue table.
- **L2-3: no repair located.** The runbook bullet is byte-identical to baseline `8937dec`.
  It was RAISED to should_fix by the refuter, so it is not disposable as a nit. Searched:
  all `needs_pin_commit` hits in the runbook, `TASK_QUEUE.md`.
- **EDQ-L2-1 is closed against the wrong head and a differently-sized module** (15 methods
  vs 13 at baseline), with no head pin in the log.
- **The canonical-suite log from the same quiet slot as the crash-matrix log has never been
  located** — anomaly A-3 named two missing logs and only one was re-custodied.
- **EDQ-L2-2 has no closure evidence at all**; the dress rehearsal that would produce it is
  recorded **OPEN**, gated on the frozen `_v2` alpha pack.
- **L2-EDQ-1 remains "qualification open"** by the council's own addendum wording, and
  **WO-CRASHMATRIX-RELIABILITY has no completion entry** in the Completed Queue table.
- **TASK_QUEUE A5 (`WO-DETECT-PULSES-BUDGET`) is still `PARTIAL; READY [AGENT]`** even though
  its cure is on `origin/main`; the hand-authored evidence note explicitly declines to retire
  it, and that note still describes the superseded **100,000**-cell budget rather than
  D-143's 165,000.
- **The detection budget value has already been falsified once by live data** (100k → 165k,
  D-143). The seat should decide whether a single n=34 sweep is an adequate basis for the
  replacement.
- **Runtime probes were NOT executed by this assembler** (read-only mandate): P2, P4, and P7
  are static-analysis claims awaiting execution. The 289 figure is a `def test_` count that
  reproduces the loader total exactly at `fac87d1` — but it is not itself a
  `countTestCases()` run at the current head.
