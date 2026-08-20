# ROW L7 — SEAM READER B (producer/consumer graph derived from ACTUAL RUNS, EXECUTION lens) — GATING seat, charter v2 full-tier

> **Assembler note (mechanical, not adjudicated).** This row attaches evidence and names candidate
> dispositions. It does **not** grade the seat READY. The verdict's standing caution binds:
> "**The work-order program is NOT CERTIFIED COMPLETE** … every seat's evidence universe was
> self-nominated, and the one denominator adversarially tested fell"
> (`docs/process_traces/2026-08-15-readiness-council/council-verdict.md:18-22`).

**Tree state at assembly.** Read-only worktree `…/scratchpad/wtS0`, branch
`impl/r2-s0-mint-resolver`, **HEAD `b92b43d`** — one commit past the `4597ad4` the task brief and
`raw/CHANGE-UNIVERSE-BRIEF.md:4` name, and 29 past the `d10881b` in `_ASSEMBLER-BRIEF.md:12`.
**`8937dec..HEAD` is 215 commits, not 214.** `origin/main == main == 0099382`. The entire Phase-2
transaction (`_v3` packs, freeze-0003 family, D-146/D-147/D-148/D-149) is **BRANCH-ONLY**.

**AMENDMENT (post-assembly).** The worktree HEAD moved again while this row was being written —
`b92b43d` → `7305e0d` → `45e0229` → `48f337b` → **`2243137`** (now 219 commits from `8937dec`).
Verified: `git diff --name-only b92b43d..2243137 | grep -E '^(joulewise|scripts|configs)/'` returns
**NOTHING** — no code, script, pack, registry or config bytes changed, so every code and config
citation in this row holds at `2243137`. The four new commits touch `README.md`, `RUN_STATE.md`,
`TASK_QUEUE.md`, `WINDOW_STATUS.md`, `docs/decision_log.md`, `docs/process/state_kernel.json`, and
`docs/process_traces/2026-08-19-prep-sprint/**`. **A seat should re-verify the doc line numbers
cited from `RUN_STATE.md`, `TASK_QUEUE.md` and `docs/decision_log.md`, which those commits edited.**
That the audited tree advanced four times during a single assembly pass is itself material to the
Phase-3 "audit at a pinned head" discipline.

---

## 0. Seat identity and 2026-08-15 result

| Field | Value | Citation |
|---|---|---|
| Seat ID | `L7-SEAM-READER-B-EXECUTION` | `sitting-packet-FINAL.md:17` (packet hash `1657a255f951b7f4`) |
| Tier | GATING | `sitting-packet-FINAL.md:29` |
| Recorded verdict | **NOT_READY** ("component: the execution-derived seam graph") | `sitting-packet-FINAL.md:29`; `raw/L7-triage.md:7`; seat report §7 `seat-reports/L7-SEAM-READER-B-EXECUTION-report.md:86-92` |
| Coverage | **21 / 25** (evidence_universe_count = 25) | `sitting-packet-FINAL.md:29`; `raw/L7-triage.md:8`; seat report §1 `:39` |
| Findings | 3 = **0 blockers** / 2 should-fix / 1 nit | `sitting-packet-FINAL.md:29`; `raw/L7-triage.md:9` |
| Falsifiers | 7, **all refused** | `sitting-packet-FINAL.md:29`; seat report §3 `:59-68` |
| Unexecuted obligations | 7 | `sitting-packet-FINAL.md:29,228-234` |
| ED-QUALIFICATION rows | 3 | `sitting-packet-FINAL.md:29,187-189` |
| Coverage adversarially tested? | **NO** | `council-verdict.md:18-22` |

The seat's own summary of what its graph proved (relevant to weighing everything below):
"The graph itself is strong: 1,478 tests green, 7 executed falsifiers all refused, **zero
producerless required outputs at the current head**, digests and off-repo custody bytes verified to
the manifest. What is missing is exactly the two items above — both fail-closed protected, both
cheap, both needed before a funded night can proceed as documented."
(`seat-reports/L7-SEAM-READER-B-EXECUTION-report.md:92`). L7 is the execution half of the charter's
paired independent seam readers; it did **not** read L6's output (`:3`).

**Phase-3 status note the seat should hold in view:** the verdict names L7 in the *minimum* set for
the Phase-3 focused re-audit — "focused re-audit of pack/custody-bearing seats (**L1, L5, L7
minimum**)" (`council-verdict.md:102-104`). That re-audit is a separate obligation from this row.

---

## 1. FINDINGS — original text verbatim, with citation

### F1 — [should_fix] Frozen PACK-namespace evidence is consumed at arm/verify/consume without its declared monotonic horizon being checked — and all 33 frozen receipts' horizons have ALREADY lapsed

- **severity:** `should_fix`
- **title (verbatim):** `Frozen PACK-namespace evidence is consumed at arm/verify/consume without its declared monotonic horizon being checked — and all 33 frozen receipts' horizons have ALREADY lapsed`
- **file_line (verbatim):** `joulewise/arm_readiness.py:2957 (also arm at 3628 and verify/consume at 3801 vs freeze-time enforcement at 3021-3027)`
- **failure_scenario (verbatim):**

> Council declares READY; Ed arms tonight on the un-rebooted machine. _freeze_evidence_for_arm re-authenticates the 33 pack evidence receipts by bytes + boot session only (now_monotonic_ns never passed), so the arm proceeds even though every receipt's valid_until_monotonic_ns lapsed ~2.8h before my probe (verified live: now=1.997e15 ns > valid_until=1.9868e15 ns on the same boot, 33/33 across the three packs). A later reviewer reading the receipt bytes finds attestations consumed past their own declared validity — the readiness chain is impeachable post-hoc, the exact 'output that neither traces cleanly nor fails closed' the charter hunts. Either the horizon must be enforced on the arm path (which then mandates a pre-arm re-author + re-freeze ceremony, since the current evidence is void) or PACK-namespace valid_until must be authoritatively documented as freeze-time-only semantics before any arm consumes these bytes.

- **Citation:** `raw/L7-triage.md:12-14`; sitting packet §4 `sitting-packet-FINAL.md:145`; seat report §4 FINDING 1 `:72`; execution-graph edge 2 `:46`; universe row U4 `:14`, U12 `:22`.
- **Post-verdict adjudication:** NOT struck. Same code seam as **L6-N3** (graded nit there) and the
  same live fact as **L1-B1** (graded blocker there, `sitting-packet-FINAL.md:49-51`) and
  **L6-B2** (blocker, `:44-46`). Confirmed by both cluster-A refuter lenses: contract —
  "L1-B1 expiry: CONFIRMED. Remedy corrected: in-place re-author NOT contract-valid (D-131 requires
  successor pack+custody root). Open ruling: durable-freeze-evidence vs successor-pack tool. **24h
  horizon is implementation policy, not D-134/D-137 contract text**" (`refuter-verdicts.md:4-6`);
  execution — "F1 (expiry) CONFIRMED executed: 33/33 generic receipts refuse
  `readiness_record_expired` via `_authenticate_generic_evidence_item` at live monotonic; remedy
  'partial'" (`refuter-verdicts.md:82-84`; `sol-refuter-A-execution.md` V2 observed
  `{"other_refusal": 0, "pass": 0, "record_expired": 33, "total": 33}`).
  Routed to **Phase 0 R1 ruling** (`council-verdict.md:74-75`) and **Phase 2 atomic re-freeze**
  (`:97-100`). The seat's own WO-L7-1 declares it "pre-arm, **needs magistrate ruling**"
  (`raw/L7-triage.md:26`).
- **Severity divergence on the record (for probe 4):** L7 should_fix; L6 nit for the *mechanism* and
  blocker for the *lapse*; L1 blocker. Nothing in the verdict harmonised these.

### F2 — [should_fix] Mandatory pre-arm sequence is undocumented: the runbook's E-step tool does not exist at the frozen measurement-checkout head, and advancing the checkout stales the recorded §5C dry-run receipt

- **severity:** `should_fix`
- **title (verbatim):** `Mandatory pre-arm sequence is undocumented: the runbook's E-step tool does not exist at the frozen measurement-checkout head, and advancing the checkout stales the recorded §5C dry-run receipt`
- **file_line (verbatim):** ``docs/phase_2/window_runbook.md:805-838 (author_arm_evidence_t0.py E-step) vs `git ls-tree 49dcc49 scripts` (tool absent at the frozen head); RUN_STATE.md:31-33``
- **failure_scenario (verbatim):**

> The measurement checkout /Users/edr/JouleWise-measurement-20260813 sits at 49dcc49, where scripts/author_arm_evidence_t0.py (the mandated T-0 E-step, merged in #149) does not exist and the arm generator still carries the launch-blocking 15-row ARM_ONLY gap. Arming there refuses. Arming at the current reviewed head requires advancing the checkout — which by the runbook's own staleness rule (and test test_dry_run_becomes_stale_after_later_head) voids dry-run-0001 (head-bound to the 49dcc49-era head; pack digests drifted 6246b6...->f4c02c8a... because #149 edited all three packs' generate_configs.py). No standing doc (RUN_STATE T7, ed-qualification-session.md, 70h plan) states the required sequence: advance checkout to final reviewed main -> lead re-runs the §5C dry-run to a fresh PASS receipt -> then E-steps. A tired operator following RUN_STATE's 'NO REBOOT preserves the frozen evidence' hits an unexplained refusal chain at night, or improvises.

- **Citation:** `raw/L7-triage.md:16-18`; sitting packet §4 `:146`; seat report §4 FINDING 2 `:74`.
- **Post-verdict adjudication:** NOT struck. Independently found by **L5** as a should-fix —
  "Pre-arm sequence unregistered: measurement checkout must advance and the §5C dry-run must be
  re-executed at the final head (dry-run-0001 is stale by binding)" (`sitting-packet-FINAL.md:133`)
  — and cross-confirmed on the packet side by the cluster-B execution lens, which verified
  `git cat-file -e 49dcc49a:scripts/author_arm_evidence_t0.py` exits 128 and the checkout is "still
  clean at `49dcc49a`" (`sol-refuter-B-execution.md` F5 prose). Contract lens flagged the same
  deployment state as a verification gap: "the canonical measurement checkout remains at 49dcc49
  with pack digest 6246b618…, while the audited ac3fe1d pack digest is f4c02c8a…; … Before ARM, lead
  must sync the canonical checkout through the governed reviewed-head procedure"
  (`sol-refuter-A-execution.md`, flag G1).
- Seat's own NB, preserved: "`reviewed_main` reads the *local* origin/main ref, so the un-fetched
  measurement checkout would also pass the exact-match check against a stale remote ref"
  (`seat-reports/L7-SEAM-READER-B-EXECUTION-report.md:74`).

### F3 — [nit] `joulewise reduce` writes its re-reduction artifact into the invoker's CWD by default

- **severity:** `nit`
- **title (verbatim):** `` `joulewise reduce` writes its re-reduction artifact into the invoker's CWD by default ``
- **file_line (verbatim):** `joulewise/cli.py:1873-1875`
- **failure_scenario (verbatim):**

> Observed live: reducing a TMPDIR bundle from the repo root dropped example-mock-local.summary_metrics.rereduced.0.5.2.json into the checkout. An operator reducing from the measurement checkout would dirty it — and a dirty measurement tree is itself an arm refusal. The guard against writing inside the bundle exists; a default outside the current directory (or a required --output) would remove the pollution path.

- **Citation:** `raw/L7-triage.md:20-22`; sitting packet §4 `:147`; seat report §4 FINDING 3 `:76`.
  Nits receive no refuter under C-028.

### Work orders (verbatim, both)

> - WO-L7-1 (pre-arm, needs magistrate ruling): resolve the PACK-evidence horizon asymmetry — either pass now_monotonic_ns in _freeze_evidence_for_arm (then schedule the mandatory re-author + re-freeze ceremony before ALPHA arm, since all 33 receipts are lapsed) or document PACK-namespace valid_until as freeze-time-only semantics in the runbook §5C and the receipt schema notes, with an explicit disposition recorded for the lapsed 08-13/14 receipts
> - WO-L7-2 (pre-arm, doc + checklist): add the explicit sequence to RUN_STATE/ed-qualification-session/runbook §5C entry gate: (1) advance the measurement checkout to the final reviewed merged main (clean, exact match), (2) verify boot session unchanged (DA90818C...), (3) lead personally re-runs the §5C dry-run at that head and requires a fresh PASS receipt binding the new head + new pack digest, (4) only then the E-steps; correct RUN_STATE's 'NO REBOOT preserves the frozen evidence' to name the dry-run staleness and the #149 pack-byte drift

Citation: `raw/L7-triage.md:26-28`.

### Unexecuted obligations carried by this seat (verbatim, all seven)

> - Live capture path: validate_powermetrics_fiducial --allow-live, MLX member collection, --arm-quiet-mode display arming (no sudo / no live measurement in this sandbox) — ED rows
> - tests.test_calibration_exits (2,036 s) and tests.test_calibration_writer_crash_matrix (5,317 s) — CI-exclusive modules not re-run in this seat's budget; last known green on the #149 merge CI
> - The decisive full-fixture mint proof (replay_d117_decisive.sh / test_coordinated_report_and_pin_change_refuses_against_floor_evidence) — requires a GitHub release download; no network. Skip marker observed and documented in batch B
> - Whole-window verdict and extract_detection_floors CLIs against a real collected corpus (runs/ corpora are off-repo); exercised only through their test fixtures
> - reserve_calibration_window_bracket.py --execute against the production ledger (exercised only inside the dry-run generator and tests)
> - quiet_mac_prep.sh (mutates display state)
> - a9/a10 retained characterization basis — seat 11's scope, excluded from my universe count

Citation: `raw/L7-triage.md:38-53`; `sitting-packet-FINAL.md:228-234`.

---

## 2. WHAT CHANGED SINCE 2026-08-15

### F1 — PACK-namespace horizon asymmetry — **THE ASYMMETRY IS UNCHANGED IN CODE; THE 33-RECEIPT LAPSE WAS CURED BY RE-ISSUANCE; THE RULING WENT THE THIRD WAY**

**(a) The code seam — verified at HEAD `b92b43d`, unchanged in the respect the finding names.**
`_freeze_evidence_for_arm` has moved to `joulewise/arm_readiness.py:5360` (called from arm `:6139`,
verify/consume `:6334`). It now passes `expected_boot_session_id`, plus two **new** arguments —
`expected_head_commit` and `lifecycle_registry`. It **still does not pass `now_monotonic_ns`.**
`_authenticate_generic_evidence_item` still accepts that keyword and still enforces it when supplied
(`:4269-4277`, `:4486-4497`); the arm caller simply does not supply it. The downstream defenses the
seat identified are all still the only defense: the `min`-fold building the arm receipt's
`valid_until_monotonic_ns` (`:6231-6252`), verify's `readiness_record_expired` (`:6499`), and
consumption's checks (`:7126`, `:7219`, `:7910`).
**Neither branch of WO-L7-1 was taken as written.**

**(b) What was done instead — the successor-pack route, ruled and executed twice.**

| Element | Evidence | Where it lives |
|---|---|---|
| R1 freeze-evidence lifecycle consult + cold gate | `docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/` (`consult.md`, `coldgate-adjudicator-ruling.md`, `coldgate-opus-refuter-findings.md`) | branch |
| **D-137** boot-session amendment (mismatch ⇒ `readiness_record_expired`) | `docs/decision_log.md:162` | branch |
| **D-139 A3** (Ed, 2026-08-17) — approves "chain-monotonic `freeze-0002` with explicit predecessor bindings; **existing operational horizons**" | `docs/decision_log.md:164`; packet `docs/process/ed-batch-packet.md` | branch |
| Freeze numbering | `docs/process_traces/2026-08-17-freeze-numbering-consult/`; commit `b6553fd` "WO-FREEZE-NUMBERING delta-8: replay reauthenticates the successor; v2 freeze sequences carry the predecessor" | branch |
| **D-140 / D-141** freeze-status byte semantics + registered residuals (cold gate, 3-seat concurrence) | `docs/decision_log.md:173-174`; custody `docs/process_traces/2026-08-18-freeze-semantics-coldgate/` (14 files); `docs/risk_register.md` R-019, R-020 | branch |
| **D-147** R2 mint-lane ruling → immutable `_v3` family, freeze-0003 chained to freeze-0002 | `docs/decision_log.md:170`; ONE home `docs/process_traces/2026-08-19-r1-r2-codesign/14-r2-ruling.md` | branch |
| `_v2` / freeze-0002 executed | 2026-08-18 at `/Users/edr/JouleWise-measurement-20260818`; digest table `docs/process/ed-morning-packet-2026-08-18.md:95-97`; D-143 records "freeze-0002 re-mints at the measurement checkout" (`docs/decision_log.md:166`) | branch |
| `_v3` / freeze-0003 executed | `5e38f1e`, `eb7f6c6`, `94dc3b3`, table `8b2b021`; U11 `3d05982`, `6fd8bce`, `74632e3`; custody `docs/process_traces/2026-08-19-refreeze-execution/` | **BRANCH-ONLY** |

Receipt-format change verified by reading
`configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json`:
`schema_version` is now `joulewise.arm_readiness_freeze_receipt.v2`, with a `predecessor` block
naming `freeze-0002` (`1277103b…`) and an `evidence_set_sha256`. Evidence receipts now carry
`head_commit` alongside `boot_session_id` and `valid_until_monotonic_ns`.

**(c) ⚠ THE R1 LIFECYCLE LAYER IS PRESENT IN CODE BUT DORMANT ON THE PRODUCTION PACKS.**
`joulewise/arm_readiness.py:45` defines `R1_ROW_REGISTRY_SCHEMA = "joulewise.arm_readiness_row_registry.v2"`,
and `_authenticate_generic_evidence_item` raises `EvidenceLifecycleError(… "V1_GRANDFATHERING" …)`
when a lifecycle registry is in force. But the only committed registry is
`configs/arm_readiness/d117_row_registry_v1.json` — `schema_version` `…row_registry.v1`, **no
`freeze_evidence_lifecycle` key** (verified by parsing); `git grep -l "arm_readiness_row_registry.v2" -- configs`
is empty; and `freeze-0003.json`'s `row_registry` field points at that same v1 file (sha `d248fdc5…`).
So `lifecycle_registry` and `expected_head` are `None` at arm — the new head-binding never fires.
D-148 clause 5 confirms this is open: "R1 row-registry **reserved values → COUNCIL** (Ed defers…)"
(`docs/decision_log.md:171`); `RUN_STATE.md:38-42` is the prep item to assemble that council packet.

**(d) ⚠ LIVE PROBE RUN BY THIS ASSEMBLER (read-only: `time.monotonic_ns()`, `sysctl`, and parsing committed bytes).**

```
now_monotonic_ns 2415145103251500  (= 2,415,145 s)
boot_session_id  DA90818C-9C31-45D0-8813-DEAE65FBA143   (unchanged — no reboot since the 2026-08-13 freeze)
d117_floor_qwen25_1p5b_v3       n=11  min valid_until 2468742407178458  expired=False
d117_floor_qwen25_7b_v3         n=11  min valid_until 2468774933440083  expired=False
d117_contrast_qwen25_1p5b_vs_7b_v3   n=11  min valid_until 2468792444508708  expired=False
all 33: boot da90818c-…, head_commit 1d3873bb7a37e9363202429f14587c85a0b4efc0
```

**The 33/33-lapsed fact is CURED — with ~53,597 s ≈ 14.9 hours of headroom at probe time.** The
project itself now names the horizon in plain text: `RUN_STATE.md:211` — "The S4 evidence **EXPIRES
~2026-08-20T16:51Z** and DIES ON ANY REBOOT (boot session da90818c…). **NO REBOOTS** until the mints
land or Ed chooses re-authoring." That is consistent with the receipts' `issued_at_utc`
2026-08-19T16:51:33Z + 24 h.

Two residuals against that cure: the receipts' `head_commit` `1d3873b` is **28 commits behind HEAD
and not on `origin/main`** (`git merge-base --is-ancestor 1d3873b origin/main` → false), and the
Phase-3 baseline-manifest **supersession has not been issued** (`council-verdict.md:68-70,102-104`),
so the amendment-12 exposure created by the re-freezes is still open.

**Candidate disposition:** STILL-OPEN — the lapse is cured, the ceremony was executed twice, and a
horizon disposition was ruled (D-139 A3 "existing operational horizons"); but WO-L7-1's actual
alternatives — enforce `now_monotonic_ns` at arm, **or** authoritatively document PACK-namespace
`valid_until` as freeze-time-only semantics in §5C and the schema notes — were neither of them taken,
and the "impeachable post-hoc" reading of the arm path is unchanged.

### F2 — pre-arm sequence — **SUBSTANTIALLY REPAIRED IN SUBSTANCE; ONE ORDERED DOC EDIT PARTLY UNDONE BY DRIFT**

WO-L7-2 asked for four things. Status of each at HEAD:

| WO-L7-2 element | Status | Evidence |
|---|---|---|
| (1) advance the measurement checkout to final reviewed merged main | **DONE IN FACT** — the checkout moved from `/Users/edr/JouleWise-measurement-20260813` @ `49dcc49` to **`/Users/edr/JouleWise-measurement-20260818`**, begun from transaction commit `28a0daa` | `docs/process/rehearsal-operator-card.md:3`; `RUN_STATE.md:167,241,323,355,383,398`; `docs/process/ed-morning-packet-2026-08-18.md:13`. Verified: `28a0daa` **is** on `origin/main`, and **both** `scripts/author_arm_evidence_t0.py` and `scripts/capture_t0_step.py` exist in its tree (`git cat-file -e` exits 0) — so the finding's "tool absent at the frozen head" condition is resolved at the new checkout |
| (2) verify boot session unchanged | **DONE and standing** — `DA90818C-…` confirmed unchanged by live probe; the constraint is now stated operationally | `RUN_STATE.md:211` ("DIES ON ANY REBOOT (boot session da90818c…). **NO REBOOTS**") |
| (3) lead personally re-runs the §5C dry-run at that head, fresh PASS binding the new head + digest | **DOCUMENTED, NOT EXECUTED at the live family** — the requirement is written into the runbook in the ordered form the WO asked for; no `_v3` dry-run receipt located | `docs/phase_2/window_runbook.md:340-364` ("After the final pack is committed at the reviewed HEAD, the lead creates the non-authorizing readiness rehearsal receipt…"; ":361-362" "Require its `PASS` receipt to bind the exact final reviewed HEAD and final pack digest; **any later HEAD or pack-byte change makes it stale**"); `:840-862` ("Lead live verification — desk evidence, not live-night authority (rule 1, non-delegable) … a **stale dry-run receipt**, or any identity mismatch is **NO-GO**. A lead who has not personally seen these pass on this checkout and pack has not verified; a subagent's or a prior session's pass does not transfer.") |
| (4) only then the E-steps | **DONE** — §5C now carries the ordered "Order of operations at the machine (each step gates the next)" with the frozen E-step wrapper sequence | `docs/phase_2/window_runbook.md:863-1024` |
| Correct RUN_STATE's "NO REBOOT preserves the frozen evidence" | **DONE, and correctly weakened** | `RUN_STATE.md:625-627`: "**NO REBOOT still preferred (moot for arming — evidence re-authors regardless under the ruled lifecycle** — but boot-session continuity keeps the qualification replays cheap)." Note the older, uncorrected phrasings survive at `RUN_STATE.md:694` ("NO REBOOT of the Mac preserves the frozen evidence (else cheap re-author)") and `:709`, inside superseded T6/T7 checkpoint sections |

**⚠ NEW DRIFT INTRODUCED BY THE REPAIR ITSELF.** The ordered terminal-review step at
`docs/phase_2/window_runbook.md:813` still begins `cd /Users/edr/JouleWise-measurement-20260813` —
the **retired** checkout — while the live one is `…-20260818`. An operator following §5C verbatim
attests the wrong tree. The rehearsal card (`docs/process/rehearsal-operator-card.md:30`) uses the
correct path, so the two operative documents disagree.

**⚠ THE COMMITTED REHEARSAL CHOREOGRAPHY IS ONE PACK FAMILY BEHIND.**
`docs/process/rehearsal-operator-card.md:30,38,50-110` targets `d117_floor_qwen25_1p5b_**v2**`,
while the live family is `_v3` (freeze-0003). Its own §head declares: "This is qualification
choreography evidence, **never claim evidence**" (`:3`).

**Candidate disposition:** READY-evidence-attached for the *documentation* half of WO-L7-2, with two
named drifts; STILL-OPEN for the *execution* half (no fresh `_v3` dry-run PASS located — see
ED-L7-2).

### F3 — `joulewise reduce` CWD default — **NOTHING CHANGED**

Verified by reading `joulewise/cli.py:1885-1915` at HEAD: when `--output` is absent the tool still
computes `output_path = cwd / f"{bundle_path.name}.summary_metrics.rereduced.{reducer_version}.json"`.
The only guards are (i) refusing when the CWD is inside the input bundle, and (ii) refusing when the
resolved output lands inside the bundle — precisely the guard the finding already acknowledged
("The guard against writing inside the bundle exists"). Neither remedy the finding proposed — a
default outside the current directory, or a required `--output` — was implemented.

`git log --oneline 8937dec..HEAD -- joulewise/cli.py` shows four commits (`3038eeb`, `b7e5730`,
`f16037c`, `b9c7d0a`) — all D-146 capture-era / claim-barrier / WO-LAUNCH-BINDING stage-3 work; none
touches the reduction output default. **NO-REPAIR-FOUND.**

*Note for the seat:* the pollution path the nit describes now runs into a **new** hazard class —
`b9c7d0a` added "standalone-reduce CLI-boundary authentication" and `launch_lineage` propagation to
the reduce path, so a stray re-reduction artifact in the measurement checkout is now also a
lineage-bearing artifact in a tree whose cleanliness `capture_t0_step.py`'s
`_verify_terminal_review` (`:290-296`) checks before every T-0 capture.

### Cross-cutting: work orders bearing on this seat's graph

| WO | State at HEAD | Citation |
|---|---|---|
| WO-T0-PRODUCER | **DONE** — PR #152 `a61ac92` (`origin/main`) at branch-only head `9e8936a`; `scripts/capture_t0_step.py` produces all nine T-0 inputs; **the deferred F4 honest-contract lane LANDED** as `65cc0f3` + `d8d2022` + `32cf987`, all on `origin/main`, registering the TRUSTED-OPERATOR limitation (`docs/decision_log.md:9630,9669`; `window_runbook.md:885`) | `TASK_QUEUE.md:106` |
| WO-KERNEL-RECONCILE | DONE — PR #150 `47d2645` (`origin/main`) | `TASK_QUEUE.md:104` |
| WO-MARGIN-RECORDER-AUTHZ | DONE — PR #151 `00ec3b7` (`origin/main`) | `TASK_QUEUE.md:105` |
| WO-L2-REAUDIT | DONE — `0f886d3`, coverage VERIFIED 251/251 | `TASK_QUEUE.md:102` |
| **WO-LAUNCH-BINDING** | **OPEN (A1, READY [AGENT])** — "Stages 1-3 MERGED (#156 `f392ff6`, #157 `bd333de`); calibration-side stage 2 DONE on the staged estimator branch @ `e22e658` (delta-ACCEPTED, rides the re-freeze per the Phase-2 plan); **remaining: stage 4 successor flag inside the transaction. Launch stays NO-GO**" | `TASK_QUEUE.md:536,630`; stage checkpoint `TASK_QUEUE.md:491`; custody `docs/process_traces/2026-08-15-launcher-binding-consult/`, `2026-08-15-launch-f3-consult/`, `2026-08-16-launch-f3-coldgate/`, `2026-08-15-launch-lineage-consult/`; code `e7fa8fd`, `72cd698`, `b9c7d0a`, `9d3ba21` |
| **WO-CONSUMPTION-EDGE** | **OPEN (A2, PARTIAL; READY [AGENT])** — "Code MERGED #155 (`d54db78`) … **Remaining before close: the production freeze (rides Phase 2) + the same-head production-pack L10 replay**" | `TASK_QUEUE.md:537,631`; custody `docs/process_traces/2026-08-15-consumption-edge-consult/` |

**Material to L7 specifically:** WO-LAUNCH-BINDING introduced an entire new receipt family into the
execution graph this seat enumerated (`launch_lineage.v1`, `launch_lineage_locator.v1`,
`launch_start_receipt.v1`, `launch_settle_receipt.v1`, `launch_completion_receipt.v1`,
`arm_readiness_launch_consumption.v2`) — none of which existed in the 25-item universe, and whose
seat-critical property ("Launch stays NO-GO") is asserted in a queue note rather than proven here.

---

## 3. ED-QUALIFICATION ROWS

### ED-L7-1 (verbatim)

> ED-L7-1: prewindow_check.sh --wait to READY plus quiet_mac_prep.sh on the freed quiet machine (stable capability; my execution proves the gate correctly BLOCKS while any agent fleet runs, so READY can only be demonstrated in an Ed/quiet block)

Citation: `raw/L7-triage.md:32`; `sitting-packet-FINAL.md:187`; the executed evidence behind it is
falsifier F6 and universe row U21 (`seat-reports/L7-SEAM-READER-B-EXECUTION-report.md:31,66`).

**NO CLOSURE EVIDENCE LOCATED.** Searched: `git grep -n "ED-L7-1"` over `docs/` (**zero** hits
outside the council trace); `git grep -n "quiet_mac_prep"` over `docs/process`, `docs/run_reports`,
`RUN_STATE.md` (only `RUN_STATE.md:3634,3778` — instructions inside superseded checkpoints — and
`docs/run_reports/2026-07-17-*` — pre-council); `docs/process/ed-batch-packet.md`;
`docs/process/ed-evening-checklist.md`; `docs/process/ed-morning-packet-2026-08-18.md:112-126`
(qualification ledger: **no prewindow/quiet-mac row**); `docs/run_reports/2026-08-18-t10-session.md:100-112`
(the closed-row table: **no prewindow/quiet-mac row**); `docs/run_reports/2026-08-19-t12-t13-session.md`
(**zero** matches for "prewindow"); `docs/process_traces/2026-08-18-shakedown-first-light/`;
`docs/phase_2/ed-qualification-session.md` (steps 1–6: privilege grant, sampler checklist, rail
probe, backlight, §5A tap walkthrough, chain-into-ALPHA — **no prewindow/quiet-mac step**).

**What DID change, and it makes the row harder, not easier.** WO-T0-PRODUCER's dwell hardening
landed: `scripts/prewindow_check.sh:37` now sets `MIN_CLEAN_DWELL_S=600` ("continuous clean time
required by D-134") with `INTERVAL_S=30`, and `:174-199` implement a `clean_since` monotonic
interval that **resets to −1 on any non-clean check** (`:195`) and prints
`continuous clean dwell ${clean_elapsed}/${MIN_CLEAN_DWELL_S}s`. That is exactly the L8-B2 / cluster-B
F3 remedy ("repair the wait to require ten continuous clean minutes — preferably a `clean_since`
monotonic interval", `sol-refuter-B-execution.md` F3 prose; `refuter-verdicts.md:67-68`). The
practical consequence for this ED row: reaching READY now requires **ten uninterrupted clean
minutes**, where the seat measured 60.09 s before.

**How ED-L7-1's own observation interacts with closing it at all — recorded as asked.** The row's
text states the gate "**correctly BLOCKS while any agent fleet runs, so READY can only be
demonstrated in an Ed/quiet block**." Three facts at this head sharpen that into a scheduling
constraint the seat should weigh:
1. The dwell change means the quiet block must now be ≥10 continuous minutes with **zero** agent
   processes, not ~1 minute. `prewindow_check.sh`'s agent census was itself a live L9 should-fix
   ("misses claude / codex mcp-server / t3 — printed OK while three agent processes were live",
   `sitting-packet-FINAL.md:155`), so a *passing* census is not by itself proof of quiet.
2. The project's standing operating posture is the opposite of quiet. `RUN_STATE.md:14-27` describes
   an active fan-out prep sprint; the T14-GO block (`RUN_STATE.md:60-80`) hands a five-day `/loop`
   with "never idle between blocks"; D-149 (`docs/decision_log.md:172`) charters **no-hands window
   automation** whose condition (3) is "the machine is quiet: census clean, fleet quiesced, no
   interactive use, single writer."
3. The one comparable quiet capture in the record was taken **by the lead, not Ed** — ED-Q-L9-3,
   "Captured 23:51 by the lead with all agent runs quiesced"
   (`docs/run_reports/2026-08-18-t10-session.md:110`) — which demonstrates the quiesce is achievable
   but also that closing it consumed a deliberate fleet stand-down.
   **A seat should therefore ask whether ED-L7-1 can be closed by a lead-executed quiesced capture
   under D-148 cl.4 ("QUIET WINDOWS ARE LEAD-DELEGATED", `docs/decision_log.md:171`) or whether the
   charter's ED-QUALIFICATION form requires Ed's own hands — and note that `quiet_mac_prep.sh`
   mutates display state, which is the half nearest to "hands".**

### ED-L7-2 (verbatim)

> ED-L7-2: fresh §5C lead dry-run PASS at the final reviewed head on the measurement checkout — executes the real reservation CLI --execute and the production ledger-writer lifecycle through both slots under lease (the recorded dry-run-0001 is head-stale after any checkout advance; a new PASS receipt binding the final head/digest is required desk evidence before arm)

Citation: `raw/L7-triage.md:34`; `sitting-packet-FINAL.md:188`.

**NO CLOSURE EVIDENCE LOCATED for a `_v3`-family PASS at the final reviewed head.**

*Attached partial evidence:*
- The obligation is now written in the runbook in the exact ordered form the WO asked for —
  `docs/phase_2/window_runbook.md:340-364` (the dry-run command, "Require its `PASS` receipt to bind
  the exact final reviewed HEAD and final pack digest; any later HEAD or pack-byte change makes it
  stale") and `:840-862` (lead live verification, rule-1 non-delegable, "a subagent's or a prior
  session's pass does not transfer").
- A concrete dry-run invocation is staged in the rehearsal card at
  `docs/process/rehearsal-operator-card.md:38` — but against the **`_v2`** pack and into the
  rehearsal scratch root `~/JouleWise-window-custody/ed-qual-20260817/rehearsal/…`, and the rehearsal
  it belongs to is recorded **OPEN** (`docs/run_reports/2026-08-18-t10-session.md:110`;
  `docs/process/ed-morning-packet-2026-08-18.md:126` "OPEN: the dress rehearsal (item 4) only.").
- The head has since advanced 28 commits past the `_v3` evidence's `head_commit` `1d3873b`, so even
  a `_v3` dry-run taken at S3/S5 time would now be head-stale by the runbook's own rule at `:361-362`.

**Searched:** `git grep -n "ED-L7-2"` (zero hits outside the council trace); `git grep -rn "dry-run-0"`
and `dry_run.receipts` across `docs/`; `docs/process_traces/2026-08-19-refreeze-execution/`
(`r5-issuance/`, `r6-issuance/`, `reports/`, `s2-goldens/`, `s4/`, `suite-logs/` — freeze/issuance
artifacts, no §5C dry-run receipt); `docs/process/rehearsal-operator-card.md`;
`docs/process/ed-morning-packet-2026-08-18.md`; `docs/run_reports/2026-08-18-t10-session.md`;
`docs/run_reports/2026-08-19-t12-t13-session.md`; `RUN_STATE.md`.

### ED-L7-3 (verbatim)

> ED-L7-3: live sudo powermetrics fiducial calibration seam (validate_powermetrics_fiducial --allow-live producing instrument_evidence.json consumed by the chain's §5B jq screen) — unexercisable without sudo + quiet machine; covered by the charter's sampler checklist but named here because it is the one producer->consumer edge in the §6 chain I could not execute or observe in any test

Citation: `raw/L7-triage.md:36`; `sitting-packet-FINAL.md:189`.

**CLOSURE EVIDENCE LOCATED — this is the strongest ED closure in either seam row, with caveats.**

- **The live producer ran, on the measurement Mac, with sudo, three times.**
  `docs/process_traces/2026-08-18-shakedown-first-light/05-driver-as-run.sh:55-64` — a `for i in 1 2 3`
  loop invoking
  `"$CLONE/.venv/bin/python" "$CLONE/scripts/validate_powermetrics_fiducial.py" --allow-live
  --power-policy ac_high_power --output-root "$CUST/runs/instrument_validation"` with `sleep 30`
  between. The scripted plan is at `01-protocol-scout.md:110`.
- **The consumer edge was exercised and produced an in-band number, recorded as a magistrate ruling's
  evidence.** D-143 (`docs/decision_log.md:166`): "the **maiden live capture** and three issued
  corpus members all exhaust 100k under the budgeted detector (real workload 112,205–137,189 cells,
  n=34 complete-corpus sweep) … **first-light re-derivation IN-BAND (b_fiducial 0.030878 s ∈
  [0.022741, 0.033559])**." The `b_fiducial` comparison is exactly the §5B screen quantity the ED row
  names; the re-derivation recipe against `instrument_evidence.json` is at
  `docs/process_traces/2026-08-18-shakedown-first-light/01-protocol-scout.md:136-158`.
- **Durable custody:** `~/JouleWise-window-custody/shakedown-20260818` (`RUN_STATE.md:384`);
  in-repo trace `docs/process_traces/2026-08-18-shakedown-first-light/` (5 files); session record
  `docs/run_reports/2026-08-18-t10-session.md`.

**Caveats a seat must weigh before calling this closed:**
1. The run was executed under **D-142's standing night license** as a "**D-139 nonclaim diagnostic
   shakedown**" while the WINDOW-COUNCIL-GATE's claim-window clearance was still pending — and the
   decision log itself preserves the counter-reading: "the counter-reading (gate text names no
   shakedown carve-out) is preserved in the T10 report's B-5" (`docs/decision_log.md:165`).
2. It predates the `_v3` family and the D-146 capture-pipeline-v3 flip (`docs/decision_log.md:169`),
   so the producer bytes it exercised are from a superseded capture era.
3. It is not recorded as an ED-QUALIFICATION row closure anywhere — `git grep -n "ED-L7-3"` returns
   zero hits outside the council trace, and the row does not appear in the closed-row tables at
   `docs/run_reports/2026-08-18-t10-session.md:100-112` or
   `docs/process/ed-morning-packet-2026-08-18.md:112-125`.

---

## 4. CANDIDATE DISPOSITIONS FOR THE SEAT TO ADJUDICATE

**Candidate dispositions are assembled, not adjudicated; the seat rules.**

| Item | Candidate disposition | Exactly what remains / what is attached |
|---|---|---|
| **F1** PACK-horizon asymmetry + 33 lapsed receipts | **STILL-OPEN** | Attached: successor-pack lane ruled (R1 consult, D-137, D-139 A3, D-140/141, D-147) and executed twice; freeze receipt v2 with predecessor chain; live probe shows **33/33 unexpired, ~14.9 h headroom**, same boot; `RUN_STATE.md:211` names the expiry instant in plain text. Remains: **neither WO-L7-1 branch was taken** — `_freeze_evidence_for_arm` (`:5360`) still passes no `now_monotonic_ns`, and no authoritative freeze-time-only semantics statement was located in §5C or the schema notes; the R1 lifecycle registry is **dormant** (committed registry is v1, D-148 cl.5 defers reserved values to council); evidence `head_commit` `1d3873b` is 28 commits stale and off `origin/main`; Phase-3 supersession unissued. |
| **F2** undocumented pre-arm sequence | **READY-evidence-attached (documentation) / STILL-OPEN (execution)** | Attached: checkout advanced to `…-20260818` from `28a0daa` (on `origin/main`, both T-0 tools present in its tree); boot-continuity constraint stated (`RUN_STATE.md:211`); runbook `:340-364` + `:840-862` carry the reviewed-head dry-run + staleness + rule-1 non-delegable text; §5C ordered E-step sequence at `:863-1024`; RUN_STATE's "NO REBOOT preserves the frozen evidence" corrected at `:625-627`. Remains: **no executed `_v3` dry-run PASS at the final reviewed head**; `window_runbook.md:813` still names the retired `…-20260813` checkout; the committed rehearsal card targets `_v2`; the uncorrected "NO REBOOT preserves" phrasings survive at `RUN_STATE.md:694,709`. |
| **F3** `joulewise reduce` CWD default | **STILL-OPEN — NO-REPAIR-FOUND** | `joulewise/cli.py:1885-1915` unchanged in the relevant respect: default is still `cwd / …rereduced…json`; only the pre-existing in-bundle guards. Four cli.py commits in the span, none touching it. Newly sharper because `b9c7d0a` added launch-lineage propagation to the reduce path, and `capture_t0_step.py:290-296` refuses on a dirty checkout. |
| **ED-L7-1** prewindow READY + quiet_mac_prep | **ED-ROW OPEN** | No closure evidence located anywhere. The bar **rose**: `prewindow_check.sh:37,174-199` now demands 600 s of *continuous* clean dwell with reset-on-dirty. The row's own text ("READY can only be demonstrated in an Ed/quiet block") now collides with a standing five-day `/loop` fan-out posture (`RUN_STATE.md:60-80`) and with D-149's automation, whose condition (3) presupposes the very quiet state this row must demonstrate. Seat must also decide whether D-148 cl.4 lead-delegation can close it, or whether `quiet_mac_prep.sh`'s display mutation makes it Ed's hands. |
| **ED-L7-2** fresh §5C dry-run PASS at final head | **ED-ROW OPEN** | Obligation now correctly written into the runbook; no receipt located. Staged only against `_v2` in a rehearsal recorded OPEN. Head has advanced 28 commits past the `_v3` evidence head, so any earlier receipt would be stale by `window_runbook.md:361-362`. |
| **ED-L7-3** live sudo powermetrics fiducial seam | **ED-ROW closed-with-evidence — SEAT TO WEIGH THE CAVEATS** | Live `--allow-live` execution ×3 on the measurement Mac (`shakedown-first-light/05-driver-as-run.sh:55-64`), consumer-side in-band re-derivation recorded in a ruling (D-143: `b_fiducial 0.030878 s ∈ [0.022741, 0.033559]`), durable custody `~/JouleWise-window-custody/shakedown-20260818` + in-repo trace. Caveats: run under D-142's night license as an explicitly **nonclaim diagnostic** with a preserved counter-reading on the WINDOW-COUNCIL-GATE; predates the `_v3` family and the D-146 capture-era flip; never recorded against this ED row ID. |

---

## 5. WHAT A SKEPTICAL SEAT SHOULD PROBE

1. **[MANDATORY — re-run the zero-gap producer→consumer census at the CURRENT head.]** L7's §2
   census concluded "**Zero producerless receipts found at the current head**"
   (`seat-reports/L7-SEAM-READER-B-EXECUTION-report.md:56`) at `8937dec`. **215 commits and an
   entire launch-binding receipt family have landed since.** Re-derive edge-by-edge, and require each
   edge to be *observed by running it* (the seat's own standard, `:43`), not read.
   *Falsifier:* any §12 close-out receipt kind, any `launch_*` receipt, or any `_v3`-family artifact
   whose producer is a test fixture or absent.
2. **[MANDATORY — new artifact kinds with no consumer or no fail-closed refusal.]** Diffing
   `8937dec..HEAD` over `joulewise/` + `scripts/` surfaces **≥29 schema IDs absent from L7's 25-item
   universe**, notably the whole launch family — `launch_lineage.v1`, `launch_lineage_locator.v1`,
   `launch_start_receipt.v1`, `launch_settle_receipt.v1`, `launch_completion_receipt.v1`,
   `arm_readiness_launch_consumption.v1` **and** `.v2` — plus
   `arm_readiness_freeze_receipt.v2`, `arm_readiness_row_registry.v2`,
   `arm_readiness_freeze_evidence_lifecycle_registry.v1`,
   `arm_readiness_freeze_predecessor_evidence_set.v1`, `arm_readiness_evidence_source.v2`,
   `arm_readiness_content_evidence_receipt.v1`, `arm_readiness_execution_evidence_receipt.v1`,
   `arm_readiness_execution_environment.v1`, `analysis_manifest_finalization.v1`,
   `analysis_semantics_projection.v1`, `calibration_bracket_binding.v1`,
   `calibration_observation_ledger.v1`, `detection_floor_artifact.v2`,
   `rehearsal_scratch_provenance.v1`, `test_sampler_ack.v1`.
   *Falsifier:* any of these with a producer and no machine consumer, or a consumer that does not
   fail closed on absence. **Priority target:** `rehearsal_scratch_provenance.v1` — a rehearsal-only
   provenance kind is precisely where a fixture-shaped seam hides.
3. **[MANDATORY — terminal-review-trailer remedy: CODE or described intention?]** The verdict's
   Addendum (`council-verdict.md:121-131`) orders "a lead-owned terminal-review attestation step
   whose commit the superseding manifest pins, with the measurement checkout and T-0 author operating
   at the attested commit." At this head:
   - **Verifiers are real code, fail-closed:** `scripts/capture_t0_step.py:288-317`
     (`evidence_author_t0_capture_terminal_review_missing`, requires exactly one each of
     `JouleWise-Terminal-Review: PASS` / `-Tree-Oid: <current tree>` / `-Pack-Sha256: <current pack digest>`,
     and refuses on a dirty or non-exact-match checkout) and `joulewise/arm_readiness_evidence_t0.py:931-937`.
   - **The producer is a documented human git ceremony, not a tool:**
     `docs/phase_2/window_runbook.md:812-838`; `docs/process/rehearsal-operator-card.md:30`.
   - **The manifest-pinning half is unbuilt:** `docs/process/audit-baseline-manifest.json` names no
     attested commit and still cites the 2026-08-13 arm packet at `:3`.
   *Falsifier for "delivered":* `git grep -l "allow-empty" -- scripts/` finds no attestation producer;
   and running `window_runbook.md:813` verbatim `cd`s into the **retired** `…-20260813` checkout.
4. **[MANDATORY — contract-vs-execution divergence between L6 and L7 on the same repaired seam.]**
   The two paired seam readers graded the identical code differently and neither grading was
   harmonised: **L6-N3 = nit** ("defense is one hop downstream"), **L7-F1 = should_fix**
   ("impeachable post-hoc"), while **L1-B1 and L6-B2 = blocker** for the same lapse fact. The code
   did not change; the fact did. Ask (a) which lens the repaired state vindicates; (b) whether
   re-issuing receipts without enforcing the horizon at `_freeze_evidence_for_arm` is a *cure* or a
   *clock reset*; (c) whether D-139 A3's "existing operational horizons" constitutes the
   "authoritatively documented freeze-time-only semantics" WO-L7-1 offered as its alternative branch —
   this assembler could locate no such statement in §5C or the schema notes.
   *Falsifier:* after the current headroom lapses, run arm against a `_v3` pack and inspect whether
   FREEZE_AND_ARM rows report PASS from expired evidence while `verify` refuses.
5. **Re-run the live horizon probe at sitting time** — the numbers here are timestamped to assembly:
   `python3 -c "import time; print(time.monotonic_ns())"` vs
   `min(valid_until_monotonic_ns)` over `configs/campaigns/d117_*_v3/arm_readiness.evidence/*.json`,
   and `sysctl -n kern.bootsessionuuid` vs `da90818c-…`.
   *Falsifier:* headroom ≤ 0, or a boot change — either restores F1's original fact pattern exactly.
6. **Probe whether the R1 lifecycle is live or dormant** (this is the difference between "head-bound
   evidence" and "a v1 registry that disables the new check"): parse
   `configs/arm_readiness/d117_row_registry_v1.json` for `schema_version` and a
   `freeze_evidence_lifecycle` key, then read `arm_readiness.py:5360-5395` for the `is None` path.
   *Falsifier:* registry is v1, no lifecycle block, `git grep -l row_registry.v2 -- configs` empty ⇒
   `expected_head_commit` is `None` at arm ⇒ the `1d3873b` staleness is invisible to the machine.
7. **Execute WO-L7-2's step (3) rather than reading it.** Take a fresh `_v3` dry-run at the current
   reviewed head on the measurement checkout and require `status: PASS`,
   `arm_disposition: NOT_APPLICABLE`, the reviewed HEAD and the final committed-pack digest, and the
   `calibration_pre_reserve_authorized` / `status: reserved` / `calibration_writer_arm_authorized`
   events (`window_runbook.md:846-858`).
   *Falsifier:* it cannot be taken at all while the `_v3` family is branch-only and `origin/main` is
   `0099382` — `reviewed_main`'s exact-match check has nothing to match. Also re-test the seat's own
   NB that `reviewed_main` reads the **local** `origin/main` ref, which an un-fetched checkout can
   satisfy against a stale remote.
8. **Attack ED-L7-3's closure at its two joints.** (i) Does the D-142 nonclaim-diagnostic framing
   admit the run as ED-QUALIFICATION evidence, given that the decision log itself preserves the
   counter-reading (`docs/decision_log.md:165`)? (ii) Does a fiducial captured **before** the D-146
   capture-pipeline-v3 flip (`docs/decision_log.md:169`) evidence the seam that the `_v3` chain will
   actually run?
   *Falsifier:* the barrier predicate `CLAIM_BEARING_ANCHOR_METHODS` introduced by D-146 refuses the
   pre-flip era with `capture_pipeline_superseded` — in which case the closure evidence is from an
   era the code now rejects.
9. **Test ED-L7-1's closability, not just its status.** Ask for a `prewindow_check.sh --wait` run
   reaching READY under the **new** 600 s continuous-dwell rule with a census that also detects
   `claude` / `codex mcp-server` / `t3` (the L9 should-fix at `sitting-packet-FINAL.md:155` — confirm
   whether WO-CENSUS-SEMANTICS landed that fix; it is recorded BLOCKED on ED-Q-L9-3, which has since
   been captured).
   *Falsifier:* a READY exit produced while any agent process is live falsifies the census, not the
   dwell.
10. **Re-check F3 cheaply and adversarially:** run `joulewise reduce` on a bundle from a clean
    measurement-checkout CWD and then `git status --porcelain=v1 --untracked-files=all`.
    *Falsifier:* a non-empty status ⇒ the nit reproduces, and now additionally trips
    `capture_t0_step.py`'s clean-checkout precondition (`:290-296`) — the nit has acquired an
    arm-blocking consequence it did not have at the sitting.
11. **Press the seat's own unexecuted obligations forward.** Five of seven remain unexecuted by this
    seat: `tests.test_calibration_exits` (2,036 s) and `tests.test_calibration_writer_crash_matrix`
    (5,317 s) were "last known green on the **#149** merge CI" — **eight PRs and 215 commits ago**;
    the decisive full-fixture mint proof now HAS an execution record (ED-QUAL-L4-1,
    `DECISIVE REPLAY: OK`, 13,180.653 s, `~/JouleWise-window-custody/ed-qual-20260817/decisive-replay.log`),
    which the seat should fold in; the whole-window verdict / `extract_detection_floors` CLIs against
    a real corpus and live `reserve_calibration_window_bracket.py --execute` remain fixture-only.
    *Falsifier:* a re-run of either CI-exclusive module at HEAD that is not green.

---

## 6. OPEN ITEMS FROM THIS ROW

- **F1 — the horizon asymmetry is UNCHANGED IN CODE.** `_freeze_evidence_for_arm`
  (`joulewise/arm_readiness.py:5360`) still authenticates PACK evidence by bytes + boot session and
  **still passes no `now_monotonic_ns`**; the min-fold (`:6231-6252`) plus verify (`:6499`) and
  consume (`:7126,7219,7910`) remain the sole defense. **Neither branch of WO-L7-1 was taken** — no
  arm-path enforcement, and no authoritative statement of PACK-namespace `valid_until` as
  freeze-time-only semantics located in runbook §5C or the receipt schema notes.
- **No explicit recorded disposition for the original lapsed 08-13/14 receipts was located** — the
  WO's other half. The `_v1`/`_v2` packs still sit in the tree beside `_v3`; whether their lapsed
  evidence is retired, grandfathered, or merely superseded is not stated in any document this
  assembler found.
- **The R1 freeze-evidence lifecycle exists in code but is DORMANT.** The only committed registry is
  `joulewise.arm_readiness_row_registry.v1` with no `freeze_evidence_lifecycle` block, so
  `lifecycle_registry` and `expected_head_commit` are `None` at arm and the `V1_GRANDFATHERING`
  refusal never fires. D-148 cl.5 defers the registry's reserved values to a council that has not sat.
- **The `_v3` evidence's `head_commit` `1d3873b` is 28 commits behind HEAD `b92b43d` and is not on
  `origin/main`** — invisible to the machine while the lifecycle registry is dormant.
- **The horizon will lapse again.** Live probe: ~53,597 s ≈ 14.9 h of headroom at assembly, on boot
  `da90818c-…`, with `RUN_STATE.md:211` naming the instant (~2026-08-20T16:51Z). The 24 h re-run
  obligation is standing and is not scheduled as a window-day step in runbook §4/§5C.
- **F2 — no executed fresh §5C dry-run PASS at the final reviewed head on the `_v3` family was
  located.** The obligation is now correctly documented (`window_runbook.md:340-364,840-862`); the
  execution is not evidenced.
- **`docs/phase_2/window_runbook.md:813` still names the RETIRED measurement checkout
  `/Users/edr/JouleWise-measurement-20260813`** in the ordered terminal-review step, while the live
  checkout is `/Users/edr/JouleWise-measurement-20260818`. Two operative documents disagree on the
  path; run verbatim, §5C attests the wrong tree.
- **The committed rehearsal choreography (`docs/process/rehearsal-operator-card.md`) targets the
  `_v2` pack family while the live family is `_v3`**, and self-declares "qualification choreography
  evidence, never claim evidence" (`:3`).
- **RUN_STATE's corrected reboot text coexists with two uncorrected copies.** The WO-L7-2 correction
  landed at `RUN_STATE.md:625-627`, but "NO REBOOT of the Mac preserves the frozen evidence" survives
  verbatim at `:694` and a variant at `:709` inside superseded checkpoint sections.
- **F3 — `joulewise reduce` still defaults its re-reduction artifact into the invoker's CWD.**
  `joulewise/cli.py:1885-1915`; neither proposed remedy implemented; four cli.py commits in the span
  touched other things. Newly consequential: `b9c7d0a` put launch-lineage on the reduce path and
  `capture_t0_step.py:290-296` refuses on a dirty checkout, so the pollution path is now arm-blocking.
- **ED-L7-1 — NO CLOSURE EVIDENCE LOCATED**, and the bar rose: `prewindow_check.sh:37` now requires
  600 s of *continuous* clean dwell with reset-on-dirty (`:174-199`). Its own text confines the
  demonstration to an Ed/quiet block, which collides with the standing five-day `/loop` fan-out
  posture (`RUN_STATE.md:60-80`) and with D-149's automation preconditions. **Unresolved: whether
  D-148 cl.4 lead-delegation may close it, or whether `quiet_mac_prep.sh`'s display mutation reserves
  it to Ed's hands.** The census this row depends on carries its own unlanded L9 should-fix
  (`sitting-packet-FINAL.md:155`, WO-CENSUS-SEMANTICS recorded BLOCKED).
- **ED-L7-2 — NO CLOSURE EVIDENCE LOCATED.** The only staged dry-run is `_v2`, into rehearsal scratch,
  inside a rehearsal recorded **OPEN**; and it would already be head-stale by `window_runbook.md:361-362`.
- **ED-L7-3 — closure evidence located but never recorded against the row**, and it carries three
  caveats: taken under D-142's night license as a **nonclaim diagnostic** with a preserved
  counter-reading on the WINDOW-COUNCIL-GATE (`docs/decision_log.md:165`); it predates the D-146
  capture-pipeline-v3 flip and the `_v3` family; and it appears in no ED-row closure table.
- **None of the three ED row IDs appears anywhere in the repository outside the 2026-08-15 council
  trace.** `git grep -n "ED-L7-1\|ED-L7-2\|ED-L7-3"` over `docs/` returns zero hits elsewhere — there
  is no mechanical tracker binding these rows to closure evidence, and the charter's READY-CANDIDATE
  form requires "all ED-QUALIFICATION rows closed" (`RUN_STATE.md:4054`; `council-verdict.md:54-57`).
- **This seat's 21/25 coverage denominator was never adversarially tested**, and at least 29 schema
  IDs — including the entire WO-LAUNCH-BINDING receipt family — entered the chain after it was
  enumerated. Under `council-verdict.md:18-22` it must be independently re-enumerated before any
  READY finding, and **L7 is named in the Phase-3 focused re-audit minimum set** (`:102-104`), which
  has not occurred.
- **Two work orders touching this seat's graph are OPEN with launch explicitly NO-GO:**
  WO-LAUNCH-BINDING (A1 — "remaining: stage 4 successor flag inside the transaction. **Launch stays
  NO-GO**", `TASK_QUEUE.md:536,630`) and WO-CONSUMPTION-EDGE (A2, PARTIAL — "Remaining before close:
  the production freeze (rides Phase 2) + the same-head production-pack L10 replay", `:537,631`).
- **Five of L7's seven unexecuted obligations remain unexecuted**, including two CI-exclusive modules
  whose "last known green" is the **#149** CI — eight PRs and 215 commits stale.
- **The entire Phase-2 transaction this row depends on is BRANCH-ONLY** on
  `impl/r2-s0-mint-resolver`; `origin/main == main == 0099382` contains none of the `_v3` packs,
  freeze-0003 receipts, or D-146/D-147/D-148/D-149.
- **Packet-metadata discrepancies to correct on the record:** the brief names HEAD `4597ad4` /
  `d10881b` and "214 commits"; the tree is at `b92b43d` with **215** commits from `8937dec`.
