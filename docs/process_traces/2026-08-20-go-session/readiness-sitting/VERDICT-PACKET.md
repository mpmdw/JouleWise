# READY-CANDIDATE COUNCIL SITTING — MECHANICAL VERDICT PACKET
**Assembled 2026-08-20 by the verdict-form aggregator (dictated-fills: assembled and flagged, NOT ruled).**
Ruled head **`5bd7acf`** (all twelve seats attach to it). Baseline **`8937dec`**; **237** commits between
(packet says 214 — seat-P.md:4, seat-L6.md:6; `rows/ROW-L6.md` says 215 — seat-L6.md:294).
Charter form: `docs/process/instrument-readiness-audit-charter.md` amendments 10–13 (lines 70–97).
Vocabulary mapping applied throughout: seat "STILL-OPEN" → charter **NOT-READY(+work orders)**;
a declared coverage/verification gap → charter **UNVERIFIED** (carried separately, §4).

---

## 1. VERDICT TALLY (charter vocabulary)

| Seat | Charter verdict | Coverage line | Single strongest reason (seat's own) |
|---|---|---|---|
| **L1** Authority plane (gating) | **NOT-READY** + UNVERIFIED | 40/42; `L1-COVERAGE` UNVERIFIED (seat-L1.md:21,40-44) | The final D-148.5 ruling requires `_v3` to lapse and a fresh `_v4` re-freeze; no READY may treat a deliberately retired armability window as live (seat-L1.md:223). |
| **L2** Calibration acquisition (gating) | **NOT-READY** (seat said STILL-OPEN) + UNVERIFIED | 251@`fac87d1` → **289** at head; 2/289 execution-probed; adversarial set 29 modules/1365 tests (seat-L2.md:2) | The false-clean coverage cure is numerically invalid at the exact merged head, before the 21 extra candidate modules (seat-L2.md:25). |
| **L3** Capture + telemetry (gating) | **NOT-READY** (seat's own `charter_component_disposition`) + UNVERIFIED | **14/21** UNVERIFIED; old 25/29 not reusable (seat-L3.md:22-26,235) | `_stop_process` still SIGKILLs only the relay; executed falsifier F-B left a SIGTERM-ignoring sampler grandchild alive with no census (seat-L3.md:225, V3:132). |
| **L4** Quantitative claim pipeline (gating) | **NOT-READY** + UNVERIFIED | 31 modules / 1,243 methods enumerated, **40** executed (seat-L4.md:2) | The receipt validator accepts a current-head **truncated two-cell** margin receipt after its internal inventory SHA is repaired, with no frozen-pack comparison (seat-L4.md:2,7). |
| **L5** Pack/readiness/custody (gating) | **NOT-READY** + UNVERIFIED | 22/22 examined, **2 fully discharged**; `L5-COVERAGE` UNVERIFIED (seat-L5.md:15,23,59) | No armable family exists — `_v3` is lapsed by ruling, `_v4` unminted, un-dry-run, uncustodied (seat-L5.md:67). |
| **L6** Seam A / contract (gating) | **NOT-READY** (8 findings, 7 unrepaired) + **explicitly disqualifying UNVERIFIED** | U1 35/35, U2 29/29, U4 10/10; **U3 ~40 of 140 schema IDs** → UNVERIFIED (seat-L6.md:41-59) | B2 was never repaired (cure was fresh data, not machinery), the data dies today, and `window_runbook.md` has **zero** `_v3`/`freeze-0003` hits vs `_v2`×10 and `…-20260813`×9 (seat-L6.md:24-30). |
| **L7** Seam B / execution (gating) | **NOT-READY** + UNVERIFIED | **0/7** clearance items READY; prior 21/25 UNVERIFIED; 57 schema IDs in changed hunks (seat-L7.md:14,19,45) | L7's mandatory independent Phase-3 re-enumeration and adversarial coverage attack were never run (seat-L7.md:53). |
| **L8** Operator + recovery (gating) | **NOT-READY** (+9 WOs) + UNVERIFIED | **22/31**; prior 24-item denominator adversarially broken (≥9 of 31 omitted ≈29%); own denominator un-attacked, "treat 22/31 as a floor" (seat-L8.md:30,58,65-67) | The operator path to a legal launch has never been walked once end-to-end (ED-Q-L8-2 has no custody root), and the first executed probe at the merged head found it broken — a `window.env` authored from §4+§6 **refuses at the very first capture** (seat-L8.md:326-335). |
| **L9** Environmental census (gating) | **NOT-READY** + UNVERIFIED | 11/17 re-inspected, 6 unexecuted, **READY discharge 0/17** (seat-L9.md:2,9) | Arm-time census still treats normal resident macOS processes as forbidden while its sole repair WO is authoritatively `blocked` on an unmet hard precondition (seat-L9.md:7). |
| **L10** Sacrificial lifecycle (gating) | **NOT-READY** + UNVERIFIED | 17/18 examined; a9/a10 off-repo unreadable; `L10-COV` UNVERIFIED (seat-L10.md:22,165) | No same-head production-pack lifecycle receipt exists, and the only frozen family examined (`_v3`) is ruled to lapse (seat-L10.md:27). |
| **L11** Retained characterization (NON-GATING) | **NOT-READY** + UNVERIFIED | `L11-COV-1` blocker: no re-enumeration, no falsification attack, no L11 re-audit dir (seat-L11.md:26-29,188) | The paper's whole-window PASSED basis remains unreproducible outside prose while its only named operational corroboration (ED-L10-1) is open (seat-L11.md:208). |
| **P** Program rows + ED roll-up | **NOT-READY** recommended, with UNVERIFIED carried distinctly | 54/54 dispositioned, **36/54** with an executed probe at `5bd7acf` (seat-P.md:11-20) | Amendment 11's three conjuncts each fail independently on program evidence alone, before a single seat row is read (seat-P.md:389-402). |

**Mechanical tally: 11 gating seats + 1 non-gating + 1 program roll-up = 13 reports, 13 NOT-READY, 13 UNVERIFIED coverage lines, 0 READY.**
(Per-finding READY dispositions exist — L1-F2/F3/F7, L5-F5, L11-SF1/SF2, L3 ED-L3-2/-4, L4-L4-1 — but no seat aggregates to READY.)

---

## 2. WORK-ORDER UNION (deduped; 62 items)

Coverage key: **QUEUE** = live row in `TASK_QUEUE.md` current queue / `state_kernel.json`; **HAND** = hand-authored `TASK_QUEUE.md` section, not in the kernel queue; **_v4** = inside the D-148.5 r3 transaction contract; **NEW** = no queue row anywhere.
Mechanical check executed at `5bd7acf`: `grep -c` for `WO-L1-|WO-L3-|WO-L4-|WO-L5-|WO-L6-|WO-L7-|WO-L8-|WO-L9-|WO-L10-` in `TASK_QUEUE.md` **and** `state_kernel.json` → **0 in both, for all nine prefixes**. `WO-L2-` → 1 hit, and it is `WO-L2-REAUDIT` in *Completed Queue Items* (`TASK_QUEUE.md:103`) — i.e. already delivered and now stale (its 251 is 289).

### (a) GATES ON *HOLDING* THE NEXT SITTING — 6 items

| # | Work order | Seat(s) | Sev | Cover |
|---|---|---|---|---|
| H-1 | **Sequence the sitting relative to the `_v4` transaction.** P dissents from D-148.5 R-2's "merge wave → sitting → `_v4`" and would invert the last two (seat-P.md:425-432). Ruling required — see §5 C-4. | P | blocker (form) | NEW |
| H-2 | **SUPERSEDE the audit-baseline manifest** (worded as supersession, never re-pin): ruled head + live pack digests + all three ruled fields (`pack_digest_algorithm`, chain-template note, per-binding paths). Executed justification: **all three pinned `_v1` digests MISMATCH at `5bd7acf`** (seat-P.md:53-76). | P(P-2/A-2/A-2b), L1(BASELINE/F1), L4(F2), L5, L6(F2 leg 4), L10(COV), L11(F1) — **7 seats** | blocker | NEW |
| H-3 | **Charter v3** folding the READY-CANDIDATE/ENUMERATING sitting-type amendment (0 hits in the charter today), or a recorded ruling that `council-verdict.md` is the operative amendment carrier; **repoint the kernel `WINDOW-COUNCIL-GATE` clearance string** at language that exists (seat-P.md:100-112). Until cured, charter:77 binds literally and 20 of 23 ED rows violate it. | P(P-4/A-4), L6(form note :16-22) | blocker (form) | NEW |
| H-4 | **Seal the packet properly:** custody under `docs/process_traces/<date>-readiness-council/`; conform to `scripts/validate_gate_packet.py`'s grammar (Charter pin + Exhibit manifest — **0 hits** in `ready-packet/`); extraction script committed beside it; reconcile the two assemblies; fix 13→**14** program rows; convene a fresh rule-11 cold pairing (seat-P.md:179-202). | P(P-9/A-12) | blocker (form) | NEW |
| H-5 | **Freeze the head with the fleet quiesced and record the SHA**; record `b9e197a` as bookkeeping-only/instrument-scope-empty; correct "214 commits" → **237** (seat-P.md:284-293; seat-L6.md:93-103; seat-L3.md:200-202; seat-L10.md:147-149). | P(P-13), L6(F1 res.1), L3(F1), L10(F2) | blocker (form) | NEW |
| H-6 | **Home the three same-signature "drafting-mechanic" consequences, (a) first** — the mechanical rule-11 trigger enumeration that blocks packet finalization; **this packet was finalized without it** (seat-P.md:114-127). `grep -rln drafting-mechanic docs/ .claude/` → council log + two packet dirs only. **Standing escalation trigger declared met and REFERRED, round three.** | P(P-5/A-5) | blocker (process) | NEW |

### (b) GATES ON *PASSING* — 33 items

**b.1 Program-level (P seat, items 6–14 of its minimal set)**

| # | Work order | Seat(s) | Sev | Cover |
|---|---|---|---|---|
| B-1 | **Re-enumerate all eleven evidence universes at the ruled head + one adversarial falsely-clean attack** on whichever row reads cleanest; re-run L2's specifically (251→289). Only one re-audit dir exists (`2026-08-15-l2-reaudit`) (seat-P.md:38-51). | P(P-1/A-1) + every seat's COV finding | blocker | NEW (predecessor row `WO-L2-REAUDIT` is COMPLETED and stale) |
| B-2 | **Per-finding disposition ledger for all 23 sweep findings**; resolve B7 (claim-bearing, P1 — `draft-v1.md:124/364/388` 8.611855 J vs `:367/375` 1.869502 J); re-run the sweep at the ruled head (last one 237 commits stale) (seat-P.md:129-149). | P(P-6/A-6) | blocker (UNVERIFIED) | NEW |
| B-3 | **Close the ED gate — 20 rows.** Critical path named: ED-Q-L8-2, ED-Q-L9-3's committed fixture, ED-L3-2 (≈1 min machine time), ED-Q-L8-4, ED-L7-1/-2, EDQ-L2-2, and ED-L10-1 (needs a scope ruling first) (seat-P.md:452-456). | P(P-8/A-14b) + all seats | blocker | partial: only ED-Q-L9-3's *dependent* is queued (A4) |
| B-4 | **Close or formally re-dispose the four Phase-1 WOs on the kernel.** "Launch stays NO-GO" cannot coexist with a verdict that is condition (1) of an automatic launch (seat-P.md:204-219). | P(P-10/A-7) | blocker | **QUEUE** — A1 `WO-LAUNCH-BINDING` (queued), A2 `WO-CONSUMPTION-EDGE` (partial), A4 `WO-CENSUS-SEMANTICS` (blocked), A5 `WO-DETECT-PULSES-BUDGET` (partial) |
| B-5 | **Audit the D-149 no-hands path as its own lens; build the mechanical GO evaluator; reconcile kernel and runbook into ONE launch model** including the self-contradictory `state_kernel.json:3338` fence ("Ed still launches") vs the three window rows' auto-GO fence (seat-P.md:295-318; seat-L1.md:78-80; seat-L3.md:77-81; seat-L8.md:314; seat-L6.md:269-273). | P(P-14/A-14), L1(NF1), L3(D149), L8(WO-L8R-8), L6(F8) | blocker | evaluator = **HAND** (`TASK_QUEUE.md:373` WO-D149-GO-EVALUATOR, not in kernel queue); lens audit + reconciliation = NEW |
| B-6 | **Rule the two M-2 residues in writing:** composed-verdict item 2d (RULING-REQUIRED, no ruling exists outside the m2-coldgate dir) and a per-pack M-2 retirement determination for `_v3`/`_v4`; **correct the generator's `--check` message**, which still prints "unfrozen draft" for `_v3` (seat-P.md:78-98; seat-L5.md:55). | P(P-3/A-11), L5(F4) | blocker + nit | NEW |
| B-7 | **End-to-end T-0 pass at the exact reviewed head (Opus W8) before any successor arm packet**; neither located (seat-P.md:151-169; seat-L6.md:215-226; seat-L8.md:307). | P(P-7/A-10), L6(F5/WO-L6-G), L8(WO-L8R-1) | blocker | NEW |
| B-8 | **Record the P-12 form ruling** — *acceptance RELABELS, it does not DISCHARGE*; refresh `CLAIMS_STATUS.md` (stamped 2026-08-16 under a 2026-08-19 banner); register the check-to-grant limitation in `docs/risk_register.md` where L4 found it absent (seat-P.md:239-266). | P(P-12/A-15) | blocker (form ruling) | NEW |
| B-9 | **Correct `WINDOW_STATUS.md:2-4`**, which asserts the evidence-expiry/no-reboot hazard "RESOLVED" — **false at `5bd7acf`** (seat-P.md:140-145). Same class as B1. | P(P-6 new #1) | blocker | NEW |

**b.2 Seat work orders (deduped across seats)**

| # | Work order | Seat(s) | Sev | Cover |
|---|---|---|---|---|
| B-10 | **Retarget `window_runbook.md` off `_v2` / `/Users/edr/JouleWise-measurement-20260813`** (10 + 9 hits, incl. `window.env` literals `:189-204` and the terminal-review `cd` at `:815`) onto the live family/checkout, and make the retarget a **named step of every family transaction**; fold in a §-numbered repeatable refresh lane. | **L6(WO-L6-A)**, L7(F2), L8(F6/WO-L8R-2), L10(L10-3), L2(L2-3 adjacent) — **5 seats** | blocker | NEW |
| B-11 | **Reconcile §4/§6 with `_ENV_KEYS`**: the executed `ARM_RECEIPT`/`LAUNCH_MANIFEST` "unknown" refusal (seat-L8.md:77 P3), the chain `REPO=` literal, the family/checkout re-pin. Defect-shaped regression: a lint parsing the runbook's own §4 block + §6 chain template against `_ENV_KEYS`. | L8(WO-L8R-2) | blocker | NEW |
| B-12 | **Pass `now_monotonic_ns` at BOTH freeze-replay call sites** (`arm_readiness.py:5253-5262`, `:5385-5392`) — or register a limitation that `FREEZE_AND_ARM` rows may report PASS from expired evidence and bar D-149 auto-GO from reading row verdicts. Regression = probe B (refusal at `valid_until + 1`). **Severity re-graded nit → blocker** (seat-L6.md:248-281). | L6(WO-L6-B) | blocker (re-graded) | NEW |
| B-13 | **Resolve the ED-QUAL-L6-1 contradiction** — re-scope to D-148.5 B-4's ceremony or reclassify T0. Lieutenant-forbidden; charter interpretation (seat-L6.md:314-322,371). | L6(WO-L6-C) | blocker (form) | NEW |
| B-14 | **Measured-run process census + process-group teardown** so a SIGTERM-ignoring sampler grandchild cannot survive `_stop_process`; executed reproduction at head (seat-L3.md:225-227). | L3(F1) | blocker (escalated) | NEW |
| B-15 | **`WO-CENSUS-SEMANTICS`**: maintenance/browser/monitor census patterns still refuse `mds_stores`, `SafariLaunchAgent`, `watchdogd` (executed V3, seat-L9.md:11-13). | L9(F1,F2), L8(F16 adjacent) | blocker | **QUEUE** — A4, `blocked` pending ED-Q-L9-3 |
| B-16 | **`prewindow_check.sh:150` check-8 pattern → `codex\|claude\|t3\|mcp-server`.** L8 executes the miss (P1) and argues the A4 blockage is a scheduling artifact: this is a regex edit, not census semantics (seat-L8.md:133,309; seat-L9.md:17). **Ruling needed on unblocking — see §5 C-6.** | L8(WO-L8R-3), L9(F3) | should-fix (raised from nit by L8) | QUEUE-adjacent (blocked under A4) |
| B-17 | **Governed `reauthor-clean` with shape verification + receipt** — replaces the raw `/bin/rm -r --` over three `$PACK_ID`-interpolated namespaces at `window_runbook.md:1017`; `grep reauthor-clean` → 0 hits in `scripts/`/`joulewise/`/queue/kernel (seat-L8.md:130,310). | L8(WO-L8R-4) | blocker | NEW (never-built WO-L8-8) |
| B-18 | **Make the 300 s fuse operator-visible**, with its licensed recovery; plus r3 B-1's environment-noise refusal reading and r3 B-3's halt-trigger bounds. **Zero** operator-visible hits today (seat-L8.md:81 P7, :129, :311). | L8(WO-L8R-5) | blocker | NEW |
| B-19 | **Regenerate the rehearsal against the armable family + obtain the lead-approved committed scratch-ledger ruling, then EXECUTE ED-Q-L8-2**, folding ED-Q-L8-4 in as E-7a and resolving F16 (seat-L8.md:312). | L8(WO-L8R-6), P(B-3 critical path) | blocker | NEW (Ed-hands leg → §2d) |
| B-20 | **Delta re-run of the 22-cell (A–V) error-injection matrix** against the rewritten §5C/E-9b/E-9c/E-10/FD-198/capture-era surface — the seat's own instrument, stale (seat-L8.md:289-292,313). | L8(WO-L8R-7) | blocker | NEW |
| B-21 | **Successor / recut arm packet** carrying paste-ready E-9a/b/c literals, horizon, fuse, re-author rule, E-14 `date(1)` literal, F12 ABORT row; sequenced behind B-7. Only arm packet is byte-unchanged since 2026-08-13 20:21 (seat-L8.md:78 P4, :125, :307; seat-L6.md:215-226,375). | L8(WO-L8R-1), L6(WO-L6-G), L7(F2) | blocker | NEW |
| B-22 | **Give `window_duration_margins_receipt.v1` a frozen-pack binding AND a machine consumer**, or delete §11's ordering obligation. **Two seats, split severity — see §5 C-2.** L4 executed: a truncated two-cell receipt validates after only its internal SHA is repaired (seat-L4.md:2 V5, :17); L6: `git grep -ln window_duration_margins_receipt` → writer only (seat-L6.md:227-232,376). | L4(L4-3), L6(WO-L6-H) | **L4: should-fix (but named its strongest reason); L6: nit** | NEW |
| B-23 | **Stage-1 `floor_mint_pin_requirements.v2`**: commit an instance + an absence check, or rule that D-147's resolver supersedes the two-stage design and delete the dead constant (`mint_floor_artifact_generalized.py:64`, `schema_v2.json:976`). Absence is still silent (seat-L6.md:194-203,373). | L6(WO-L6-E) | should-fix | NEW |
| B-24 | **Hashed post-collection backup receipts** in `scripts/backup_runs.sh` for both roots (0 sha256 hits; 0 commits across all 237), or amend §12 `:1807-1810`. Fold in L10's `bundle_count=5`-for-3-bundles miscount at `backup_runs.sh:31` (seat-L6.md:205-213,374; seat-L10.md:173). | L6(WO-L6-F), L10(L10-5) | should-fix + nit | NEW |
| B-25 | **`PRIVILEGE_INSTALLATION`**: build the producer or delete the four `privilege.*` rows as dead code — **decided before any `clock_route ≠ MANUAL`** (seat-L6.md:234-246,377). See §5 C-1 for the GIT_CHECKOUT half. | L6(WO-L6-I) | nit | **_v4** (r3 B-2 assigns it `NO_R1_AUTHORING_LANE`) |
| B-26 | **Typed refusal for an absent ledger parent** — current probe exits 1 with a raw `FileNotFoundError`, not a registered refusal — plus an exact-route regression (seat-L2.md:13). | L2(L2-2) | should-fix | NEW |
| B-27 | **Scope the `needs_pin_commit` runbook bullet** (`window_runbook.md:453`), byte-identical to baseline, telling the operator the condition ends the attempt without its valid pre-slot relation (seat-L2.md:15). | L2(L2-3) | should-fix | NEW |
| B-28 | **Refresh the kernel status for the detection-budget work order** — code is cured (165,000-cell/120 s fail-closed, 2 regressions in 9.192 s) while `state_kernel.json:3308` still says `partial`/"MERGE-STAGED" though `e22e658` is an ancestor (seat-L2.md:11; seat-P.md:214). | L2(L2-1), P(P-10/A-8) | bookkeeping | **QUEUE** — A5 |
| B-29 | **D-118 gate-ledger mechanical checker**: D-118 asserts mechanical enforcement; no checker in `scripts/` or `.github/` (seat-L1.md:52-56,207). | L1(F4/S1) | should-fix | NEW |
| B-30 | **Kernel freshness**: `updated: 2026-08-19` at a 2026-08-20 head, and `gen_state.py:216` validates format only — an in-memory stale-date falsifier passed (seat-L1.md:57-62,209). | L1(F5/S2) | should-fix | NEW |
| B-31 | **`FREEZE-FCM01.md:5` still forbids registering the estimator in any pack while the active `_v3` calibration files register it** — reconcile or supersede (seat-L1.md:63-68,211). | L1(F6/S3) | should-fix | NEW |
| B-32 | **Invariant 8** still accepts a textual `D-041` substring (falsifier passed against `gen_state.py:368`) and still names retired P2-006 (seat-L1.md:69-73,215). | L1(F8/N2) | nit | NEW |
| B-33 | **`WO-L3-2` checklist home**: `ed-qualification-session.md:17` step 2 points at a checklist-free module docstring and `/tmp` staging instead of `scripts/ed_session/sampler-checklist.sh`. **Never queued** (seat-L3.md:229). | L3(F2) | should-fix | NEW |
| B-34 | **`WO-L3-3` 100 ms leg**: qualification captures at 1 Hz (`sampler-checklist.sh:108` `-i 1000`) while primary 100 ms bundles realize 0.112–0.114 s; no rollover/drain-budget/sample-count re-derivation. **Never queued** (seat-L3.md:231). | L3(F3) | should-fix | NEW |
| B-35 | L3 nits: related-work SoC boundary wording; `samplers_available` echoes the requested list (seat-L3.md:233). | L3(F4,F5) | nit | NEW |
| B-36 | **PR #149 hosted Actions-log retrieval + runbook cleanup note** for the bytecode-pollution limb (F1's two unproven limbs; `gh` unreachable in-seat) (seat-L5.md:37,49). | L5(F1) | should-fix | NEW |
| B-37 | **`freeze-0003` + U11 receipts bind no `plan_tree`, and preserve-mode `--check` copies checked-out bytes into its generated comparison** (`generate_configs.py:1942-1950`) — the echo hole; the mutation falsifier is still unexecuted (seat-L5.md:19,51; V6 `plan_tree` count = 0). **Apparent conflict with L1/L6 — see §5 C-3.** | L5(F2) | blocker | NEW |
| B-38 | **`_v1` packs still exit 0 saying "unfrozen draft"** (`generate_configs.py:185-192,268-278`) (seat-L5.md:21,55). | L5(F4) | nit | NEW |
| B-39 | **`reduce` writes by default into the invoker CWD** (`cli.py:1885`) — executed reproduction created `bundle.summary_metrics.rereduced.0.6.0.json` in CWD; can dirty a measurement checkout (seat-L7.md:20,47). | L7(F3) | should-fix | NEW |
| B-40 | **One-home hazard register / `WO-L9-4` is unregistered** — searches hit only descriptions of its absence (seat-L9.md:19). Charter seat 9 is a *hazard register + completeness disposition* (charter:48-50). | L9(F4) | should-fix | NEW |
| B-41 | **Mid-workload CPU-contention detector, or a documented uncontrolled-limitation in the paper** — `evaluate_cpu_idle_admission` is a pre-run gate only (`idle_admission.py:392`) (seat-L9.md:21). | L9(F5) | should-fix | NEW |
| B-42 | L9 nits: JW-MET-2's four literals have no named §12 custody destination; `POWER_PREFLIGHT` has no charge-state gate/disposition; lid state is operator discipline with no probe (seat-L9.md:23-27). | L9(F6,F7,F8) | nit ×3 | NEW |
| B-43 | **Runbook extraction command omits the co-required `--consumption-semantics-id`** (`window_runbook.md:1766`), exits 2 as enforced at `extract_detection_floors.py:101` (seat-L10.md:167). | L10(L10-2) | should-fix | NEW |
| B-44 | **`FLOOR-BIND-01` same-custody fence still live; no prospective cross-session licence; no CLI transcript for salvage / supersession / v2 aggregate-mint / waiver** (seat-L10.md:171). | L10(L10-4) | should-fix | **QUEUE** — A10 `FLOOR-BIND-01` READY |
| B-45 | **SF3 retained re-derivation artifact / recovered whole-window verdict**, and strip uncaveated PASSED prose at `decision_log.md:4684` and `README.md:102`; `CLOSE_OUT.md:6-7` is prose while extraction records `whole_window_neg8_verdict_missing` (seat-L11.md:190). | L11(SF3) | should-fix | NEW |
| B-46 | **`draft-v1.md:189` still says freeze-0003 "is not yet minted"** though all three S5 mints are ancestors of `5bd7acf` (seat-L11.md:192; independently found by seat-P.md:146). | L11(L11-NEW-1), P(P-6 new #2) | should-fix | NEW |
| B-47 | L11 nits: `a9 MANIFEST.sha256:202` names an absent `./backup.log` with no `PRUNED.md` entry; D-054's unreproduced 0.007 J / 24.9 ms (80–87%) prose at `decision_log.md:4689,4693` (seat-L11.md:198-200). | L11(N1,N2) | nit ×2 | NEW |

### (c) `_v4`-TRANSACTION ITEMS (ride D-148.5 r3's contract) — 12 items

| # | Item | r3 clause / seat | Note |
|---|---|---|---|
| V-1 | Registry install at the `_v4` boundary (v2 registry + `freeze_evidence_lifecycle`) — dormant R1 today; activating on `_v3` would refuse all 33 receipts (`head_commit 1d3873bb…` vs `reviewed_main() 5bd7acf…`) | R-2; seat-L6.md:174-185, seat-L7.md:39, seat-L1.md:31 | mechanism independently reproduced by L6 |
| V-2 | `EXECUTION_ENVIRONMENT_FINGERPRINT_EXACT_AT_REUSE` + `evidence_author_environment_changed` in `_authenticate_existing_r1` | r3 B-1 | operator-surface consequence is **B-18** (unhomed: seat-L8.md:83 P9) |
| V-3 | `NO_R1_AUTHORING_LANE` token + `_SUPPORTED_ENVIRONMENT_COMPARISONS`, policy `r1.execution_bound.no_r1_lane_24h.v1` | r3 B-2 | **conflicts with L6's GIT_CHECKOUT disposition — §5 C-1** |
| V-4 | V5 values install as status-quo defaults; first D-139 shakedown IS the measurement | r3 B-3 | fuse invisibility = **B-18** |
| V-5 | **MECHANICAL halt-trigger gate in the window scheduler** (T-0→arm ≤ 15 min; p99 arm→consume ≤ 4 min) — "prose halt triggers are how stop signals get eaten" | r3 B-3; seat-L8.md:83 P9, :261-266 | **absent from `scripts/` and `joulewise/`** — executed |
| V-6 | Clean-arm dry run redefined: `dry-run` + file-09 P1/P2/P3, **no real arm for ceremony** | r3 B-4 | **makes ED-QUAL-L6-1 unsatisfiable as written — §3, §5 C-5** |
| V-7 | Envelope arithmetic pricing (a) Ed's step-6 turnaround and (b) published-head canonical-suite green time; likely pre-mint horizon raise | r3 B-5 | **needs ED-QUAL-L6-2's observed lane duration — expires ~17:00Z today (§3)** |
| V-8 | Publication-refusal anchored at runsheet STEP 6 | r3 B-6 | — |
| V-9 | A-1 option (a) pricing: schema+consumer pre-mint, marker instance fuse-bound | r3 B-7 | — |
| V-10 | **GAMMA `_v3` prospective manifest returns 4 validator refusals** (`analysis_prospective_schema_invalid, _unknown_key, _unresolved_slot, _not_frozen`) — remedy belongs in `_v4` bytes, not a `_v3` patch | seat-L4.md:15 V4; seat-L10.md:161 | executed |
| V-11 | Current-family dry-run / arm / consumption custody (only `_v1 dry-run-0001` @ `49dcc49` exists) | seat-L5.md:20,53; seat-L7.md:17 | |
| V-12 | Full `_v4` lifecycle transcript captured at ONE final head (L10's closure criterion) | seat-L10.md:161 | |

### (d) ED-OWED (hands / privilege / quiet-bench) — 11 items

| # | Item | Seat(s) | Deadline |
|---|---|---|---|
| E-1 | **`-getusingnetworktime` sudoers one-liner (or a ratified alternative)** — executed P2 at head: `sudo: a password is required`. A **hard precondition of any D-149 auto-GO window**, not a convenience (seat-L8.md:76,227,315; `RUN_STATE.md:59-63` T16). | L8 | before any auto-GO window |
| E-2 | **The rehearsal hour (ED-Q-L8-2)** — "the program's most valuable Ed hour", unspent; no custody root exists; mechanism must be rebuilt `_v4`-bound (seat-L8.md:228,312; seat-P.md:339-341). | L8, P | `_v4`-bound |
| E-3 | **Genuinely quiet ~12-min re-run of ED-Q-L8-3** (both halves ran inside the 3 h 40 m decisive replay, with a charge transition mid-sequence) (seat-L8.md:229; seat-L9.md:32). | L8, L9 | — |
| E-4 | **Live `quiet_mac_prep.sh` (ED-Q-L8-4)** — zero execution artifacts; promoted to blocker-precondition by F16 (seat-L8.md:230). | L8 | — |
| E-5 | **ED-Q-L9-3 agent-free recapture + committed regression fixture** — the single largest unclosed dependency; gates A4 `WO-CENSUS-SEMANTICS` (seat-L9.md:15; seat-P.md:342-346). | L9, P | — |
| E-6 | **ED-L3-2 SIGTERM-grace observation** — ≈1 minute of machine time (seat-P.md:453). L3 grades it READY on 10 custody bundles (4.7–22.8 ms) — **disputed, §5 C-7**. | P vs L3 | — |
| E-7 | **EDQ-L2-2 production-checkout §5C rehearsal + D-134 dry-run receipt at the reviewed head**; non-delegable (seat-L2.md:21). | L2, L7(ED-L7-2) | `_v4` head |
| E-8 | **EDQ-L2-1 crash matrix on the quiet bench at the audit-baseline head** — the tracked log is 15 tests at a head where both `ac3fe1d` and `8937dec` have 13 (seat-L2.md:19). | L2 | quiet bench |
| E-9 | **ED-QUAL-L1-1 production-Mac `generate_arm_readiness.py verify` + `project_identity_pins.py verify` positives** (seat-L1.md:181-183). | L1 | `_v4`; **same-boot — perishable on reboot** |
| E-10 | **ED-QUAL-L4-1 custodied decisive replay at the reviewed `_v4` head** (existing one predates r5/r6 and `_v3`) (seat-L4.md:11). | L4 | `_v4` |
| E-11 | **Pre-fuse `_v3` rehearsal-lane wall-clock harvest** (ED-QUAL-L6-2 / WO-L6-D) — r3 B-3 names it "the only pre-commitment measurement opportunity" and r3 B-5 requires the number for the `_v4` envelope arithmetic (seat-L6.md:324-339,372). | L6 | **~17:00Z TODAY** |

---

## 3. ED-ROW RECONCILIATION (23 rows)

**Baseline tally (packet `30-ED-QUALIFICATION-rows.md:986`): 3 CLOSED · 12 PARTIAL · 8 OPEN · 0 SUPERSEDED.**
**Seat-P re-tally at `5bd7acf`: unchanged in substance** — independently confirmed by
`find ~/JouleWise-window-custody -maxdepth 2 -newermt "2026-08-19"` → **empty**; zero rows closed since assembly (seat-P.md:324-327).
**Seat-P forward tally: 2 durable CLOSED / 21 not** — the `_v4` re-freeze uncures ED-QUAL-L1-2 by construction, and ED-QUAL-L1-1 / ED-QUAL-L6-2 / EDQ-L2-2 / ED-L7-2 all bind pack identity or a reviewed-head dry-run (seat-P.md:347-354).

| # | Row | Packet | Owning seat's grade | Δ |
|---|---|---|---|---|
| 1 | ED-QUAL-L6-1 | OPEN | **OPEN — "not closable as written"** (seat-L6.md:304) | **UNSATISFIABLE-AS-WRITTEN** |
| 2 | ED-QUAL-L6-2 | PARTIAL | **OPEN**, deliverable absent (seat-L6.md:324) | seat harsher; **EXPIRES TODAY** |
| 3 | ED-QUAL-L1-1 | PARTIAL | **UNVERIFIED** (seat-L1.md:46-50,219) | vocabulary shift; same-boot ⇒ perishable |
| 4 | ED-QUAL-L1-2 | CLOSED (branch-only) | **CLOSED as historical capability, "not current arm authority"** (seat-L1.md:219) | branch-only caveat CURED by merge (seat-P.md:330-332); `_v4` will uncure |
| 5 | ED-QUAL-L5-1 | PARTIAL | **STILL-OPEN → NOT-READY** (seat-L5.md:24,61) | seat harsher |
| 6 | EDQ-L2-1 | PARTIAL | **PARTIAL / not closed** (seat-L2.md:19) | agree; sibling's "log not locatable" is **stale** — log tracked at `3f9d759` |
| 7 | EDQ-L2-2 | OPEN | **OPEN** (seat-L2.md:21) | agree |
| 8 | ED-L3-1 | PARTIAL | **NOT-READY** — WO-L3-2/-3 don't exist (seat-L3.md:241) | seat harsher |
| 9 | ED-L3-2 | OPEN | **READY (narrow SIGTERM-relay observation only)** (seat-L3.md:29,243) | **DISAGREEMENT — §5 C-7** |
| 10 | ED-L3-3 | PARTIAL | **UNVERIFIED** — negative CPU differential; note lead-restored (seat-L3.md:245) | vocabulary shift |
| 11 | ED-L3-4 | PARTIAL | **READY as of this audit** — parser accepted live plist; `Mac15,9`/`25F84` matched live (seat-L3.md:247) | **DISAGREEMENT** (packet: "no recorded binding anywhere") |
| 12 | ED-L7-1 | OPEN | **OPEN** (seat-L7.md:43) | agree |
| 13 | ED-L7-2 | OPEN | **OPEN** (seat-L7.md:43) | agree |
| 14 | ED-L7-3 | PARTIAL | **PARTIAL / UNVERIFIED — not a closure** (seat-L7.md:51) | agree |
| 15 | ED-L10-1 | OPEN | **OPEN** (seat-L10.md:23-27,163) | agree; **may be UNSATISFIABLE — needs a scope ruling** (seat-P.md:455-456; seat-L10.md:141-142) |
| 16 | ED-QUAL-L4-1 | CLOSED (pre-r5/r6) | **UNVERIFIED — cannot close an "at audited head" row at `5bd7acf`** (seat-L4.md:11) | **DISAGREEMENT** — seat-P spot-verified the primary (`DECISIVE REPLAY: OK`) and keeps CLOSED with caveat (seat-P.md:333-335) |
| 17 | ED-Q-L9-1 | CLOSED | **closed with evidence** (seat-L9.md:31) | agree; off-repo, unhashed, mutable setting, no T-0 re-check |
| 18 | ED-Q-L9-2 | PARTIAL | **"closed for documentation-grade execution, qualified"** (seat-L9.md:32) | **DISAGREEMENT** — L8's P6 places both halves inside the decisive replay (seat-L8.md:80,229) |
| 19 | ED-Q-L9-3 | PARTIAL | **OPEN — hard precondition unmet** (seat-L9.md:15,33) | seat harsher; gates A4 |
| 20 | ED-Q-L8-1 | PARTIAL | **PARTIAL — not closed as written** (seat-L8.md:227) | agree w/ consolidated file; `rows/ROW-L8.md` said CLOSED → fail-open |
| 21 | ED-Q-L8-2 | OPEN | **OPEN** (seat-L8.md:228) | agree |
| 22 | ED-Q-L8-3 | PARTIAL | **PARTIAL** (seat-L8.md:229) | agree; `rows/ROW-L8.md` said CLOSED → fail-open |
| 23 | ED-Q-L8-4 | OPEN | **OPEN — and now blocker-adjacent** (seat-L8.md:230) | promoted by F16 |

**Rows where seats disagree with the packet or each other (5):** #9 ED-L3-2 (L3 READY vs packet OPEN vs P critical-path-owed), #11 ED-L3-4 (L3 READY vs packet PARTIAL), #16 ED-QUAL-L4-1 (L4 UNVERIFIED vs P/packet CLOSED), #18 ED-Q-L9-2 (L9 qualified-closed vs L8 contaminated/PARTIAL), plus #20/#22 where `rows/ROW-L8.md` scored CLOSED and both L8 and the consolidated file score PARTIAL (seat-L8.md:169-179,210-214).

**Ruled UNSATISFIABLE-AS-WRITTEN (1, + 1 candidate):**
- **ED-QUAL-L6-1** — the row demands "a same-boot `generate_arm_readiness.py arm` reaches row evaluation"; D-148.5 **B-4** excludes any real arm from the ceremony ("the first real arm of the `_v4` family is the shakedown window's own"), so it cannot close until the first funded window — while charter:70-77 says stable rows are performed BEFORE the sitting and cannot be deferred. **Council must re-scope or reclassify T0** (seat-L6.md:314-322).
- **ED-L10-1** — candidate: D-148.7's barrier may have made its specified positive proof structurally impossible; nobody has adjudicated (seat-P.md:455-456; seat-L10.md:141-142).

**Rows expiring TODAY / perishable:**
- **ED-QUAL-L6-2 / the pre-fuse `_v3` rehearsal harvest — expires with the fuse ≈2026-08-20T16:51–17:00Z.** L6's live probe at 12:26:09Z measured headroom 15,924 / 15,957 / 15,974 s ≈ **4.42 h** (seat-L6.md:151-157). r3 B-3 names it "the only pre-commitment measurement opportunity"; r3 B-5 requires that duration for the `_v4` envelope arithmetic. If unharvested, the envelope gets **estimated** — the exact substitution the row exists to prevent (seat-L6.md:332-339).
- **ED-QUAL-L1-1** — same-boot row; boot session `DA90818C-…` still live but dies on any reboot (seat-L6.md:154; packet row 3).
- Whole-family perishability: every pack-bearing ED closure is `_v4`-invalidated (seat-P.md:347-354).

---

## 4. UNVERIFIED REGISTER — mandatory re-audit obligations (distinct from work orders)

Charter:66-68: *"A zero-finding report without the full packet is UNVERIFIED, not READY."* Amendment 11 makes UNVERIFIED **independently disqualifying**. These carry a **re-audit** obligation, which work orders do NOT discharge (seat-P.md:417-421).

| # | Gap | Numbers | Seat |
|---|---|---|---|
| U-1 | **Ten of eleven evidence universes never re-enumerated.** `ls docs/process_traces/ \| grep -i reaudit` → **one** dir. | 1 of 11 | seat-P.md:38-51 (P-1/A-1) |
| U-2 | **L2 denominator moved.** Prior re-audit measured 251/251 at `fac87d1`; the same eight-module list loads **289** at `5bd7acf`; adversarial source-surface sweep finds **29 modules / 1,365 tests** incl. 21 outside the list; **2/289 execution-probed**. Even 289 is a lower bound. | 251 → 289 → (29 mod / 1365) | seat-L2.md:2,9 |
| U-3 | **L6 U3 schema-ID trace.** **140** `joulewise.*.vN` IDs enumerated from code (`opus-L6-scratch/schema-census.txt`); **~40 traced** (arm/T-0/freeze subset only). Post-collection, mint, launch-lineage and claims planes **not re-traced**. Seat's own prior cross-check said "~120". | 40 / 140 | seat-L6.md:43,52-59,347 |
| U-4 | **L1 coverage** — no sealed independent re-enumeration or adversarial coverage artifact at head; 2 production-Mac verify groups unexecuted. | 40 / 42 | seat-L1.md:21,40-44 |
| U-5 | **L3 coverage** — old 25/29 unusable (mixed-unit, predates the D-146 v3 capture change); 7 units unexamined. | 14 / 21 | seat-L3.md:22-26,235 |
| U-6 | **L3 D-146 capture-era delta re-audit** — the four-site v3 flip is merged with **no L3 delta re-audit**. | — | seat-L3.md:71-75,237 |
| U-7 | **L4 coverage** — 31 modules / 1,243 test methods enumerated; 40 unique methods executed. Replaces (does not inherit) the old 24/27. | 40 / 1,243 | seat-L4.md:2,9 |
| U-8 | **L5 coverage** — no independent focused L5 re-audit or adversarial coverage attack; `WO-L5-1..3` untracked in queue/kernel; 16/18 denominator unusable. | 2 discharged / 22 | seat-L5.md:23,59 |
| U-9 | **L7 coverage** — mandatory Phase-3 re-enumeration + adversarial attack **never run**; changed hunks expose **57** schema IDs vs the self-nominated 25-item universe. | 0/7 clearance READY | seat-L7.md:19,45 |
| U-10 | **L8 coverage** — prior 24-item denominator **adversarially broken** (omits ≥9 of 31 items ≈29%); seat's own 31 is self-nominated and **un-attacked**; "treat 22/31 as a floor". | 22 / 31 | seat-L8.md:30,58,65-67 |
| U-11 | **L9 coverage** — 6 of 17 surfaces unexecuted; **READY discharge 0/17**; the module's ordinary fixture fakes all `pgrep` results absent, so the suite **cannot falsify** the blocking defect. | 11 / 17 | seat-L9.md:2,9,43 |
| U-12 | **L10 coverage** — a9/a10 corpus off-repo and unreadable; no independent re-enumeration or coverage attack located; 447 changed files / 68,247 insertions in scope. | 17 / 18 | seat-L10.md:22,165 |
| U-13 | **L11 coverage** — no L11 re-enumeration, no READY-falsification attack, no L11 re-audit dir. | — | seat-L11.md:26-29,188 |
| U-14 | **The 23-finding sweep is formally UNVERIFIED as a body** — no per-finding verification ledger at `5bd7acf`; only B4 ever adjudicated (REFUTED). Sweep is 237 commits stale and already misses two live defects. | 1 / 23 adjudicated | seat-P.md:129-149 (P-6/A-6) |
| U-15 | **Seat-P's own P-1 limb** — P did not re-enumerate any seat's universe; explicitly recorded as an unexecuted obligation and the reason P-1 blocks. 36/54 of its own items carry an executed probe. | 36 / 54 | seat-P.md:25-33 |
| U-16 | **L2's crash-matrix concurrent-load characterization not repeated** (quiet-bench measurement, barred during an agent session). | — | seat-L2.md:2 F4, :29 |
| U-17 | **L11 canonical-suite discovery returned no terminal footer** (started twice); excluded from any passing claim. Same class as L3's `test_powermetrics_fiducial` non-terminal result. | — | seat-L11.md:177-181; seat-L3.md:204-208 |

**Mechanical consequence:** 13 of 13 reports declare at least one UNVERIFIED line. Amendment 11's "no UNVERIFIED" conjunct fails 13 times over.

---

## 5. CROSS-SEAT CONFLICTS REQUIRING A MAGISTRATE RULING

**C-1 — L6's "GIT_CHECKOUT is not a gap" vs ruling r3 B-2's no-lane census.**
L6 executed a producer census over all 29 evidence kinds: *"exactly two kinds have no producer module — `PRIVILEGE_INSTALLATION` and `GIT_CHECKOUT`. I ruled `GIT_CHECKOUT` **not a gap**: its row `desk.reviewed_checkout` is satisfied by an arm-time internal pass (`arm_readiness.py:6181,6401` `internal_passes.add("desk.reviewed_checkout")`), which is a legitimate producer route"* (seat-L6.md:234-241).
Ruling r3 B-2 assigns **all four** declarative kinds (incl. `GIT_CHECKOUT`) the token `NO_R1_AUTHORING_LANE`, with the cold-final respelling: *"two of the four kinds HAVE producers at :3919/:5775; what all four lack is a generic R1 authoring lane"* (`MAGISTRATE-RULING-r3.md:38-47`). The base ruling's corrected census (terra's) says *"GIT_CHECKOUT + PRIVILEGE_INSTALLATION have no authoring lane (predicate map only)"* (`MAGISTRATE-RULING.md:74-78`).
**These answer different questions and must not be allowed to cancel each other:** L6 answers *"does the evidence kind have a producer route?"*; r3 B-2 answers *"is there a generic R1 authoring lane where the comparison is consulted?"* On r3's own terms `GIT_CHECKOUT` has **neither** a producer module nor a lane — L6's disposition rests solely on the arm-time internal pass. **Ruling needed:** does an arm-time `internal_passes.add` satisfy the seam-A producer obligation, and if so does that change the `NO_R1_AUTHORING_LANE` row text for `GIT_CHECKOUT` in the `_v4` install? A silent merge of the two readings would let the kind pass both audits by pointing at the other.

**C-2 — L4's "SHA-repaired truncated margin receipt validates" (exact text + evidence).**
Verdict line: *"The receipt validator accepts a current-head, truncated two-cell receipt after its internal inventory SHA is repaired, without comparison to the frozen pack."* (seat-L4.md:2, `strongest_reason`).
Finding text: *"**L4-3 — SHOULD-FIX, STILL-OPEN.** The §12 close-out record retains only the receipt path and SHA, with no frozen-plan comparison [window_runbook.md:1795]. My executed SHA-repaired truncation probe confirms the validator's internal-consistency-only behavior. Failure scenario: a stale or re-pinned pack can yield a plausible PASS over a shortened census, which can then be recorded without proving it is the frozen pack. This is not cured by the merge wave."* (seat-L4.md:17).
Evidence — executed probe **V5** (seat-L4.md:2): derive the three-cell synthetic fixture, truncate `r['cells']` to 2, recompute `cell_inventory_sha256` over the truncated list, call `validate_window_duration_margins_receipt(r)` → **`TRUNCATED_SHA_REPAIRED_RECEIPT_ACCEPTED cells=2`**, exit 0. Supporting probe **V6**: `rg 'plan_tree\.sha256|pack_tree_sha256.*plan_tree' docs/phase_2/window_runbook.md` → **`NO_CLOSEOUT_FROZEN_PACK_COMPARISON`**. Locus: `joulewise/window_duration_margins.py:1032` — *"The validator receives only a receipt mapping and has no frozen-pack input"* (seat-L4.md:7).
**Is it NEW?** The *artifact* is not new — L6 filed F6/N1 against the same receipt on 2026-08-15 and re-verified it at head: `git grep -ln "window_duration_margins_receipt" -- joulewise scripts` returns **one** file, the writer (seat-L6.md:227-232). What is new is the **direction of the defect**: L6's is "no reader"; L4's is "the reader that exists **accepts a censored census**" — a **fail-open** property, executed, at the ruled head, on a §12 close-out artifact that feeds claim custody. It is also **not** covered by L4-B1's cure: PR #151 (`00ec3b7`) hardened the recorder's *read authorization*, not the receipt's *content binding* (seat-L6.md:230).
**Severity split to resolve:** L6 grades it a **nit** (WO-L6-H, "give it a machine consumer or delete §11's ordering obligation"); L4 grades it **should_fix** yet names it the seat's **single strongest reason** — an internal mismatch on its face. Under the C-028 tiering the aggregator flags this as a candidate **blocker** (executed, fail-open, claim-adjacent, no compensating consumer) and refers the severity to the magistrate. Consolidated as **B-22**.

**C-3 — L5's F2 echo hole vs L1/L6's "freeze receipts authenticate".**
L5: *"All three `_v3` freeze and projection receipts have zero `plan_tree` references… preserve-mode generation literally copies all checked-out output bytes into the temporary 'generated' tree, so `--check` compares a modified tree to itself; the underlying echo hole remains"* — blocker, mutation falsifier **unexecuted** (seat-L5.md:19,51; V6 count 0).
L6: *"all three `_v3` packs' `pack_identity.plan_sha256` reproduce **byte-exact** at `5bd7acf` … The freeze receipts authenticate at this head"* (seat-L6.md:145). L1's V4/V5 show preserve-mode `--check` passes and bare `--check` refuses, and grades the pair a pass (seat-L1.md:136-167).
**Different objects** (`plan_sha256` vs `plan_tree`), so not a contradiction — but a reader of the tally alone would take L1/L6's positive as covering L5's blocker. **Ruling needed** on whether byte-exact `plan_sha256` recomputation discharges the `plan_tree`-binding limb, and on ordering the unexecuted tamper falsifier. Note also seat-P's independent finding that **all three `_v1` pack-tree digests MISMATCH the manifest** (seat-P.md:62-72) — same machinery, opposite direction.

**C-4 — The P-seat's resequencing dissent.**
D-148.5 R-2 sequences *"merge wave → READY-candidate sitting → `_v4` transaction WITH registry install → shakedown-first windows"* (`MAGISTRATE-RULING.md:41`). Seat-P dissents: *"Hold the sitting AFTER the `_v4` transaction… I dissent on that ordering and would invert the last two — the fuse compels a `_v4` re-freeze, so a sitting held now rules every pack-bearing row and one of the three closed ED rows against a family already decided dead, and guarantees the extra baseline supersession + re-audit round Opus W2 warned of. Ruling `_v3` READY today buys a verdict with a known expiry."* (seat-P.md:425-432).
Corroborating seats: L1 (F3 "no READY may treat a deliberately retired armability window as live"), L5 (strongest reason: no armable family exists), L6 (B2 "the sitting's own verdict outlives the armability of every pack it could bless"), L8 (operator surface becomes three generations stale), L10, L4 (remedy belongs in `_v4`). **This is a reversal of a ruled sequence → rule-11 mandatory cold-pairing trigger, and the lieutenant is forbidden to decide it.**

**C-5 — ED-QUAL-L6-1 vs charter amendment 10 vs D-148.5 B-4.** See §3. Three authorities, no consistent state: the row demands a real arm; B-4 forbids a ceremony arm; charter:70-77 forbids deferring stable rows past the sitting. L6: *"Leaving it as written makes the clearance rule unsatisfiable by construction — which is a fail-open shape, because the pressure will be to quietly call it closed"* (seat-L6.md:320-322). **WO-L6-C is explicitly lieutenant-forbidden** (seat-L6.md:371).

**C-6 — L8's F16 quiet-prep false-FAIL, and the A4 blockage.**
F16 (seat-new, "blocker-shaped", seat-L8.md:136): `arm_readiness_evidence_t0.py:1056-1058` refuses if **any** `FAIL:` substring appears in `quiet_mac_prep.sh` stdout **and** requires the literal *"OK: display verification reports all online displays asleep."* — the two exclusive branches of the same `if/elif` at `quiet_mac_prep.sh:96-99`. `RUN_STATE.md:3714,:3858-3861` record that script's "Graphics capability" FAIL as **"the known false signal on this build"**, with `pmset -g log` named as the authoritative check. If it still fires, E-7a authoring refuses **deterministically and twice over**, with no documented recovery. Whether it still fires is unknown — **which is exactly what ED-Q-L8-4 exists to establish, so F16 promotes ED-Q-L8-4 from a documentation row to a blocker precondition.** L8's P10 discharges the cheap desk half (the three OK literals match verbatim).
**Rulings needed:** (i) does F16 enter the record as a blocker or as a conditional-on-E-4 item? (ii) does ED-Q-L8-4's promotion stand? (iii) **the A4 unblocking question** — L8 argues `prewindow_check.sh:150` (B-16) is "a four-token regex edit, not census semantics: the blockage is a scheduling artifact" (seat-L8.md:133,309), while the kernel holds A4 hard-blocked on ED-Q-L9-3 (seat-L9.md:2 V5). Splitting the regex edit out of A4 is a kernel-semantics change and is lieutenant-forbidden.

**C-7 — ED-L3-2: READY (L3) vs OPEN (packet, seat-P).** L3 grades it *"READY for its narrow normal-relay condition"* on ten custody bundles (post-parse minus sampling-stop 4.7–22.8 ms vs a 10 s grace), while stating it *"does not close F1's missing post-teardown census or test the SIGKILL branch"* (seat-L3.md:29,243). The packet says OPEN — *"none found; dropped from `ed-evening-checklist.md` despite `council-verdict.md:92`"* — and seat-P keeps it on the ED critical path at "≈1 minute of machine time" (seat-P.md:453). Same tension for **ED-L3-4** (L3 READY on a live parser+`Mac15,9`/`25F84` match; packet: "no recorded binding anywhere"). **Ruling needed:** may a seat close a stable ED row on *narrow-condition* evidence when the row's literal object is broader?

**C-8 — ED-QUAL-L4-1: UNVERIFIED (L4) vs CLOSED (seat-P + packet).** L4: the primary log is off-repo and the replay predates r5/r6 and `_v3`, so *"it cannot close an 'at audited head' stable row at `5bd7acf`"* (seat-L4.md:11). Seat-P opened the primary and read `DECISIVE REPLAY: OK`, keeping it CLOSED with the pre-r5/r6 caveat (seat-P.md:333-335). **The owning seat is more conservative than the roll-up.** Under the falsely-clean discipline the aggregator flags the owning seat's grade as the safe default and refers the split.

**C-9 — ED-Q-L9-2: L9's "closed for documentation-grade execution, qualified" vs L8's contamination evidence.** L9 closes it qualified (four live `sudo -n powermetrics` ABBA arms; negative CPU differential noted) (seat-L9.md:32). L8's P6 timeline-reconstructs both halves inside the 3 h 40 m decisive replay with a charge termination mid-sequence (seat-L8.md:80,229), and the packet holds PARTIAL. **Same underlying run, two dispositions.**

**C-10 — `rows/ROW-L8.md` vs the consolidated ED file on ED-Q-L8-1 and ED-Q-L8-3.** L8: *"on all six substantive divergences the sibling assembly is the more conservative and the more correct, and `rows/` errs consistently in the fail-open direction (closing ED rows that are partial, demoting a contract violation to staleness). That is the same falsely-clean signature the 2026-08-15 verdict warned about, reproduced inside the packet."* (seat-L8.md:210-214). **This is a finding about the packet itself, not only about two rows** — see §6.

**C-11 — F4 ID collision (upheld, recorded so it cannot recur).** `council-verdict.md:44-45` Disposition 4 struck "F4's timing premise"; that F4 is **L8-B3** (the `sudo -n systemsetup`/D-004 privilege finding), **not** L6-S3 (hashed backup receipts). `rows/ROW-L6.md` carries the warning; the sibling assembly does not. **Nothing in L6's row was struck** (seat-L6.md:205-213,292). A seat reading only the sibling would treat L6-S3 as struck.

**C-12 — Severity re-grades declared by seats (all require ratification; the lieutenant may not adjudicate severity downward).**
| Finding | From | To | Seat basis |
|---|---|---|---|
| L6 F8/N3 freeze-replay horizon | nit | **blocker** (WO-L6-B) | fact pattern becomes hostile by ruling at ~16:51Z; D-149 reads row verdicts (seat-L6.md:248-281) |
| L3 F1 orphan escape | (prior) | **blocker** | executed F-B reproduction + D-149 removes the observer (seat-L3.md:227) |
| L8 F13 check-8 pattern | nit | **should-fix** | B2's repair made check 8 the dwell admission test — blast radius grew after scoring (seat-L8.md:133) |
| L8 F16 | — | **seat-new, blocker-shaped** | see C-6 |
| L8 ED-Q-L8-4 | documentation row | **blocker precondition** | see C-6 |
| L4 L4-3 | (should_fix) | **candidate blocker** | see C-2 |

---

## 6. FORM DEFECTS OF THIS SITTING (these condition how the verdict may be RECORDED)

**6.1 — Packet form (seat-P P-9 / A-12, seat-P.md:179-202):**
1. **STRIKE in the packet's favour:** `scripts/validate_gate_packet.py` **EXISTS** at `5bd7acf` (580 lines, `3835288`); the claim it is "still unbuilt, so the trust anchor is manual" is **false**.
2. …which makes the rest worse: **the packet does not conform to the validator's grammar** — `grep -rl "Charter pin\|Exhibit manifest"` over `ready-packet/` → **zero hits**; the validator refuses it.
3. **No sealed custody** under `docs/process_traces/<date>-readiness-council/`. This packet lives at `docs/process_traces/2026-08-19-prep-sprint/ready-packet/`. (Confirmed: only `2026-08-15-readiness-council/` exists.)
4. **No extraction script committed beside the packet** — violates the M-2 non-author-assembly protocol, whose point is that the reviewed party here is the magistrate.
5. **No fresh rule-11 cold pairing convened** for this sitting — and charter:85-88 makes the cold pairing a requirement of **every council READY**.
6. **13-vs-14 program-row index miscount.** `grep -c "^## P-" rows/ROW-P-PROGRAM.md` → **14**; `00-INDEX.md` says "the thirteen program-level rows (P-1…P-13)" twice. **P-14 is un-indexed** and was graded only because seat-P grades un-indexed rows on principle: *"a row that exists in the packet and in no index is a row that gets adjudicated by nobody."* P-14 is itself a **blocker** (D-149 deleted the launch-authority clause; the runbook never heard).
7. **Two independent, unreconciled assemblies** (`ready-packet/` and `ready-packet-rows/`) ship in the same custody. L6 records the countervailing evidence: *"The two assemblies are jointly complete and individually incomplete: neither alone would have supported this verdict"* — an argument for keeping the duplication **deliberately**, not for shipping it unreconciled (seat-L6.md:295).
8. **Commit-count error:** packet 214, actual **237** (seat-P.md:4; seat-L6.md:6; `rows/ROW-L6.md` said 215).

**6.2 — The head was not frozen; a commit landed mid-sitting.**
`b9e197a` landed on `main` **during** the sitting. Diff is `README.md` + `RUN_STATE.md` only (2 files, +95/−15); **instrument scope is empty**, so no lens result is invalidated on content (seat-P.md:284-290; seat-L3.md:200-202; seat-L10.md:147-149).
**But the T-0 disarm consequence is real and executed** (seat-L6.md:93-103): `capture_t0_step._verify_terminal_review(...)` at `5bd7acf` raises `CaptureT0Error: reviewed checkout is dirty or differs from local/origin main`, because `arm_readiness.reviewed_main()` returns `head_commit 5bd7acf…, local_main b9e197a…, origin_main b9e197a…, clean true, **exact_match FALSE**`. L6's ruling: *"a docs-only bookkeeping commit to `main` disarms the entire T-0 producer… This is P-13's pathology recurring inside the sitting convened to cure it, and it is an availability property of the seam that no document names."* This is simultaneously (i) a form defect of the sitting and (ii) a substantive finding under B1 with a named failure scenario (seat-L6.md:383-386).

**6.3 — Seat-brief vocabulary drift (charter-form defect, recorded per the parent's instruction).**
The seat briefs asked for `READY / CONDITIONALLY-READY(conditions) / STILL-OPEN(remains)`. The binding charter (`:79-83`) **DELETED READY-WITH-CONDITIONS** and admits exactly `READY / NOT-READY(+work orders) / UNVERIFIED`. Nine of thirteen reports returned "STILL-OPEN" (L2, L3, L4, L5, L7, L8, L9, L10, L11). L6 and L8 caught it and refused the conditional verdict on the record (seat-L6.md:16-22; seat-L8.md:14-17); L3, L4, L10 supplied a charter mapping alongside. L6: *"The council should note the vocabulary drift in the seat briefs themselves — it is the same fail-open shape the charter amendment was written to close."*
**Aggregator's mapping is mechanical and lossless here:** no seat returned CONDITIONALLY-READY, so no conditional pass had to be discarded. **Seat-P independently rules the aggregate question:** *"A 'conditionally-ready' aggregate would be the deleted verdict returning under a new name, at the sitting where it is most dangerous"* (seat-P.md:404-412).

**6.4 — Fleet/charter shape.**
The charter fleet is ten gating seats + one non-gating (`charter:27-57`). This sitting ran **twelve** reports: L1–L11 plus **seat P**, a program-rows/ED roll-up with **no charter seat definition**. P is not a gating lens and its grades are program-level; it states so (seat-P.md:31). Record whether P's output is charter-conforming evidence or advisory.

**6.5 — Harness reporting defects.** `seat-L3.status` and `seat-L10.status` report `semantic_status=unknown / completion=unknown` although both reports are complete with envelopes marked `completion: complete`. Two seats (L6, L8) and P returned prose reports without the `claude-codex-report/v1` envelope. Non-substantive; recorded so the packet index is accurate.

**6.6 — Consequence for recording.** Under charter:85-91 a council **READY** requires the cold pairing over a **sealed** packet in charter-mandated custody, and amendment 12's final-head invalidation voids affected lens results on any post-baseline repo change. §6.1(3,5) and §6.2 are unmet; **the manifest's three pack digests already MISMATCH at the ruled head (seat-P.md:62-72), so amendment 12 is live against every 2026-08-15 lens result carried forward.** A **NOT-READY** aggregate does not require the cold pairing and can be recorded as charter-conforming; **any READY component could not be.** The magistrate should state explicitly whether this sitting's record is entered as **charter-conforming (NOT-READY)** or **advisory**, and §6.1's items 3–6 gate the *next* sitting either way (§2a).

---

## 7. DRAFT AGGREGATE VERDICT (mechanical, per amendment 11's conjuncts)

Amendment 11 (`charter:79-83`): *"Council READY requires: **no NOT-READY**, **no UNVERIFIED**, **all ED-QUALIFICATION rows closed with evidence**."*

| Conjunct | Required | Observed | Result |
|---|---|---|---|
| 1. No NOT-READY | 0 | **11 gating seats NOT-READY (L1–L10 gating + L11 non-gating), 12 of 12 lens reports, plus the program roll-up** | **FAILS** |
| 2. No UNVERIFIED | 0 | **13 of 13 reports declare ≥1 UNVERIFIED coverage/verification line (§4, U-1…U-17)**; L6 and L1 mark theirs *independently disqualifying* | **FAILS** |
| 3. All ED-QUALIFICATION rows closed with evidence | 23 / 23 | **3 CLOSED / 12 PARTIAL / 8 OPEN — 20 of 23 not closed**; independently re-confirmed (custody `-newermt 2026-08-19` → empty); forward tally **2 durable / 21 not** | **FAILS** |
| 4. (amdt. 11–12) Cold rule-11 pairing over a sealed packet in charter custody | required for any READY | none convened; packet outside the mandated path and refused by the validator's grammar | **UNMET** |
| 5. (amdt. 12) Final-head invalidation | no post-baseline drift | manifest pins `ac3fe1d`; **all three pack digests MISMATCH at `5bd7acf`**; `main` advanced to `b9e197a` mid-sitting | **LIVE** |

### DRAFT AGGREGATE: **NOT-READY**, with the UNVERIFIED coverage finding carried **distinctly**.

Stated mechanically, unsoftened:
- **No path to READY exists at `5bd7acf`.** Each of the three conjuncts fails **independently**, on program evidence alone, before any seat row is read (seat-P.md:389-402). Any one is dispositive; all three hold.
- **No conditional aggregate is available.** READY-WITH-CONDITIONS is DELETED. The per-seat conditioned grades (P-3, P-11, P-12, P-13) are **per-row work orders and do not aggregate** (seat-P.md:404-416).
- **The distinction between the two outcome types must survive into the record:** **NOT-READY carries work orders (§2); UNVERIFIED carries a mandatory RE-AUDIT (§4).** Coverage is the second, not the first. If the register in §4 is folded into the work-order list, the re-audit obligation is discharged by fix rounds that never re-measure a denominator — the exact fail-open this sitting exists to prevent.
- **L11 is outside the launch-GO aggregation** (charter amendment 13) — its NOT-READY does not enter conjunct 1 for launch purposes, but it does bar a defensible publication-basis claim (seat-L11.md:22,188).
- **Standing escalation trigger is DECLARED MET and REFERRED, not absorbed** (seat-P.md:123-127): round three of "stop-signal question ruled under packet-finalization pressure, consequence adopted, consequence never homed." Rule 11 says the next spend is a **CONSULT**, not another round.
- **Items the magistrate alone may rule (lieutenant-forbidden):** C-4 (reversal of the ruled sequence), C-5 / WO-L6-C (charter interpretation), C-6(iii) (kernel-semantics change to A4), C-12 (any severity re-grade, especially downward), §6.6 (charter-conforming vs advisory recording), H-3 (charter amendment), H-6 (process-rule consequence homing).

---

*Assembled mechanically from `seat-L1.md`…`seat-L11.md` + `seat-P.md` at `/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/ready-sitting/`; charter, queue, kernel and ruling probes executed read-only in `…/scratchpad/wtRC-OPUS` at `5bd7acf`. Aggregator asserts no verdict of its own; every grade above is a seat's, every conflict is referred.*
