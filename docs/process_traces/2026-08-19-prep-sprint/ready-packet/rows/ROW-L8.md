# ROW L8 — OPERATOR + RECOVERY HUMAN FACTORS (xhigh, launch-gating)

**Assembly note (read first).** This row is MECHANICALLY ASSEMBLED. Nothing below is graded
READY. Where a repair exists, its commit/PR/path is named so the seat can check it; where no
repair was located, the row says so and lists what was searched.

**Tree actually read.** `/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtS0`,
branch `impl/r2-s0-mint-resolver`, **HEAD = `b92b43d`** ("Shakedown-v3 first-light run card
(prep item 6b)…", 2026-08-19 18:50 PT). The task brief named `4597ad4` and the assembler brief
named `d10881b`; both are ancestors — `4597ad4` is HEAD~2, and two later commits (`79a4cd0`
D-149 GO-receipt template, `b92b43d` shakedown run card) are in scope and are cited below.
`main == origin/main == 0099382`; `git rev-list --count main..HEAD` = **51**; merge-base
`311d8016`. **Where evidence lives is load-bearing in this row** and is stated per item.

---

## 0. Seat identity and 2026-08-15 result

| Field | Value | Citation |
|---|---|---|
| Seat | `L8-OPERATOR-RECOVERY-HUMAN-FACTORS`, GATING, xhigh | `sitting-packet-FINAL.md:33` |
| Verdict | **NOT_READY** | `raw/L8-triage.md:6`; seat report §8 (`…/seat-reports/L8-OPERATOR-RECOVERY-HUMAN-FACTORS-report.md:139-140`) |
| Coverage | **21 / 24** (evidence_universe_count = 24; items 7 and 12 partial, item 24 unexecuted) | `raw/L8-triage.md:7`; seat report §1 table + `:38` |
| Findings | **15** (7 blockers / 5 should-fix / 3 nits); falsifiers 8 | `raw/L8-triage.md:8`; `sitting-packet-FINAL.md:33` |
| Seat question audited | "what a fatigued operator can do wrong at 2am that no receipt catches, across runbook §5/§5A/§5C, the FINAL arm packet, and the ED-session scripts, plus the 20-minute volatile-horizon implications" | seat report `:5` |
| Error-injection matrix | 22 cells (A–V): **14 C, 1 C\*, 4 P, 4 N**; the four N cells are B7 (launch license), S (`rm -r`), T (restore order), R (bounded TOCTOU by design) | seat report §3, `:68-93` |
| Council-wide verdict | **NOT-READY. 0 READY / 11 NOT-READY**; "No funded window may be armed"; work-order program **NOT CERTIFIED COMPLETE** | `council-verdict.md:12-22` |
| Sitting class | **ENUMERATING sitting** (charter:77-78 did not bind); the reconvened sitting is a **READY-CANDIDATE** sitting where charter 77-78 binds — only T0 rows may remain open | `council-verdict.md:54-57` |

**Two post-verdict adjudications bind this row specifically:**

- **Disposition 4 — L8-B4 is STRUCK.** "**Struck findings:** L8-B4 (both lenses: wrong-path
  artifact; correct fail-closed refusal), WO-L2-4 (phantom), F4's timing premise."
  (`council-verdict.md:44-45`). The "F4 timing premise" struck in the same line is **cluster-B
  refuter F4 = this seat's B3 = F3 below** — the privilege gap survived, its timing premise did not.
- **Phase 0 — L8-B7 is CONTRACT-BEARING.** "…rule-2 design consults for the prospective-manifest
  validator/finalizer and the margin-recorder authorization (Opus W6) · **L8-B7 launcher binding
  is contract-bearing (Opus W7)**." (`council-verdict.md:77-78`). It therefore required a ruling
  before code, not just an implementation.

**Refuter coverage map for this seat** (the task brief named the ECF pair; ECF covered
L10-B1/L4-B1/L9-B1/L9-B2 and contains **zero** L8 findings — verified by
`grep -n "L8" refuter-outputs/*.md`, which hits only `refuter-verdicts.md:9,42,55,125`):

| L8 finding | Refuter cluster | Contract lens | Execution lens |
|---|---|---|---|
| F1 (B1 producer) | B | `sol-refuter-B-contract.md` F1+F2 **CONFIRMED** | `sol-refuter-B-execution.md` F1+F2 **CONFIRMED** |
| F2 (B2 dwell) | B | F3 **CONFIRMED** (gap 540 s computed) | F3 **CONFIRMED** (executed replay: `READY after 1 min`, `real 60.09`) |
| F3 (B3 clock privilege) | B | F4 **CONFIRMED** | F4 **PARTIAL** — gap survives, timing premise dies |
| F4 (B4 stale freeze) | A | `refuter-verdicts.md:9-14` **REFUTED** | `refuter-verdicts.md:86-88` **REFUTED**, `identity_equal True` |
| F5 (B5 stale packet) | B | F5 **CONFIRMED** | F5 **CONFIRMED** (`git cat-file -e 49dcc49a:scripts/author_arm_evidence_t0.py` → 128) |
| F6 (B6 templates) | B | F6 **CONFIRMED** + NEW doubled plan-path defect | F6 **CONFIRMED**, all four mismatches |
| F7 (B7 launch license) | DG | `refuter-DG-out.md` F3 **CONFIRMED blocker** | `sol-out-refuter-DG.md` F3 **CONFIRMED blocker** |
| F8–F15 (should-fix / nits) | — | no refuter run assigned | no refuter run assigned |

Also folded in at the sitting: **B-execution's NEW DISCOVERY** — "baseline ac3fe1d lacks the three
JouleWise-Terminal-Review\* commit trailers the T-0 author demands
(arm_readiness_evidence_t0.py:918-930) — terminal-review evidence needs an operational producer
too; folds into the integrated T-0 repair WO" (`refuter-verdicts.md:115-117`), and the
**ADDENDUM**'s ruled remedy: "a lead-owned terminal-review attestation step whose commit the
superseding manifest pins, with the measurement checkout and T-0 author operating at the attested
commit" (`council-verdict.md:128-131`).

---

## 1. FINDINGS — original text verbatim, with citation

Source of the verbatim text: `raw/L8-triage.md` §FINDINGS (extracted from
`docs/process_traces/2026-08-15-readiness-council/triage.json`, seat entry
`L8-OPERATOR-RECOVERY-HUMAN-FACTORS`). Seat-report cross-reference in each sub-row.

### F1 [blocker] No shipped producer for the T-0 input files the evidence author requires
- `file_line` (verbatim): `joulewise/arm_readiness_evidence_t0.py:448-499,595-724 vs docs/phase_2/window_runbook.md:802-838`
- failure_scenario (verbatim):
  > Ed completes E-4…E-9 exactly as the runbook/packet write them, runs the T-0 author, and gets REFUSE evidence_author_t0_clock_attestation_missing (executed): the author consumes nine byte-canonical JSON inputs (six command captures with monotonic timestamps + clock-attestation + arm-context + launch-manifest) that no tool, no runbook step, and no packet step produces; the only 2am path forward is hand-fabricating canonical JSON with invented monotonic_ns values, which the receipts cannot distinguish from honest capture
- Seat report: §4 B1 (`:100`) — "*This is the fatigue-shaped hole: absence of tooling converts an honest operator into a forger or ends the night.*"
- **Refuter disposition:** CONFIRMED by both lenses (B-contract F1/F2; B-execution F1/F2), with two corrections adopted: (a) F1+F2 **merge into ONE work order** ("shipped T-0 acquisition/capture tool… the nine filenames are implementation preconditions, not D-134 names", `refuter-verdicts.md:64-67`); (b) B-execution's honesty amendment — "The phrase 'no human can hand-produce' is literally overstated: a human can fabricate these plain JSON objects. That worsens, rather than refutes, the authenticity defect."

### F2 [blocker] The frozen E-7b command cannot prove the ≥10-minute idle the author enforces
- `file_line` (verbatim): `scripts/prewindow_check.sh:36-37,177-198 vs joulewise/arm_readiness_evidence_t0.py:49,954-957 vs runbook:366-373,780-789`
- failure_scenario (verbatim):
  > On a well-prepared (clean) machine, `prewindow_check.sh --wait` exits READY after 3 checks × 30 s ≈ 61 s (per-check cost measured at 0.156 s); the T-0 author refuses any prewindow capture shorter than 600 s, so the better Ed prepares the machine the more certainly authoring refuses — and if the author did not enforce it, the window would launch into the XProtect idle-daemon band that cost window a9's first member, now unrecoverable because the one-launch capability makes relaunch a newly frozen session
- Seat report: §4 B2 (`:101`); executed falsifier F7 (`:58`).
- **Refuter disposition:** CONFIRMED both lenses. Contract lens computed `{'clean_exit_lower_bound_s': 60, 'author_min_idle_s': 600, 'gap_s': 540}`. Execution lens **replayed the wait loop**: `clean check 3/3` / `READY after 1 min.` / `real 60.09`. Ruled remedy: "Preserve the author's ten-minute check; repair the wait to require ten continuous clean minutes—preferably a `clean_since` monotonic interval… **do NOT lower author threshold**."

### F3 [blocker] CLOCK_PROBE needs sudo -n systemsetup, which D-004's powermetrics-only sudoers cannot satisfy
- `file_line` (verbatim): `joulewise/arm_readiness_evidence_t0.py:884-905; docs/decision_log.md:316; runbook:509-514`
- failure_scenario (verbatim):
  > At authoring time (>10 min after E-4/E-5 because E-7b's wait sits between), the interactive sudo timestamp is cold and the sudoers NOPASSWD entry covers only /usr/bin/powermetrics, so the fresh `sudo -n systemsetup -getusingnetworktime` probe exits nonzero → clock.network_time_off underivable → author REFUSE → no GO receipt, with no documented recovery at night
- Seat report: §4 B3 (`:102`).
- **Refuter disposition:** SPLIT, synthesized. Contract lens **CONFIRMED**; execution lens **PARTIAL** — "The undocumented sudo dependency is real, but the claim that the current E-7b necessarily cools the timestamp is false because E-7b currently lasts only about one minute… Once F3's 10-min dwell lands, relying on an undocumented cached credential becomes unsound and the privilege gap becomes deterministic." The council **struck the timing premise only** (`council-verdict.md:45`): "F4's timing premise (privilege gap survives inside WO-T0-PRODUCER)." Remedy already ruled: D-127's exact-path/argv sudoers (`refuter-verdicts.md:71-73`).

### F4 [blocker] Committed freeze receipt is stale — the ALPHA pack cannot arm at the audit baseline — **STRUCK 2026-08-15**
- `file_line` (verbatim): `configs/campaigns/d117_floor_qwen25_1p5b_v1/arm_readiness.freeze.receipts/freeze-0001.json (pack_identity.pack_root=/Users/edr/JouleWise-measurement-20260813/…) vs joulewise/arm_readiness.py:3604-3610`
- failure_scenario (verbatim):
  > Executed: every `generate_arm_readiness.py arm` invocation at the baseline head refuses readiness_freeze_receipt_mismatch before row evaluation, because freeze-0001.json binds the pre-#149 measurement-tree pack identity while the committed digest is now f4c02c8a…; the pack also still self-describes 'unfrozen draft / not armable' (M-2), which §5C's entry gate treats as NO-GO — a re-freeze plus magistrate ruling must precede any night
- **POST-VERDICT ADJUDICATION: STRUCK.** `council-verdict.md:44` — "**Struck findings:** L8-B4 (both lenses: wrong-path artifact; correct fail-closed refusal)". Refuter basis: `refuter-verdicts.md:9-14` (A-contract: "Mismatch was wrong-path artifact… identity_matches=True all three packs at canonical path; committed digest not a comparison input; M-2 already governs placeholder text… wrong-checkout refusal = correct fail-closed") and `:86-88` (A-execution: "canonical-path probe executed, identity_equal True at /Users/edr/JouleWise-measurement-20260813 pack; mismatch reproduces only from audit scratch path. F3 CLOSED as artifact").
- **The struck finding's SECOND clause was not struck by the same reasoning.** The M-2 "unfrozen draft / not armable" self-description was ruled to be "already governed" by M-2, and M-2 itself was **REMANDED, not adjudicated** at the sitting (`council-verdict.md:33-40`). See §2 for what happened to it.

### F5 [blocker] The FINAL arm packet's tap script is stale against the baseline runbook and would run the wrong night sequence
- `file_line` (verbatim): `~/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md §3 (frozen tree 49dcc49a, digest 6246b618) vs runbook:802-838 and manifest head ac3fe1d2/digest f4c02c8a`
- failure_scenario (verbatim):
  > The packet is expressly 'written to be executed without reading the runbook', yet it contains no T-0 authoring E-step, no 20-minute volatile horizon, no re-author rule, and expects §0.6's 'no shipped authoring route' refusal that no longer matches the shipped tooling; a tired Ed following it verbatim goes E-9 → E-9a and dead-ends (or worse, improvises) at the exact point the current runbook inserts the author step
- Seat report: §4 B5 (`:104`).
- **Refuter disposition:** CONFIRMED both lenses. Execution lens recorded the packet's sha256 `5c05f6fe99b547467372b90a61957163c47c891f6ff0c6414a4d3a7c40e47a96`, proved `git cat-file -e 49dcc49a:scripts/author_arm_evidence_t0.py` exits 128 (author absent at the packet's frozen head), and ruled: "**Merely editing the old packet would leave its frozen-head claims false**" — issue a reviewed **SUCCESSOR** packet, preserve the old as custody (`refuter-verdicts.md:74-75`).

### F6 [blocker] Runbook §4 window.env example and §6 chain template fail the T-0 author's own machine contract
- `file_line` (verbatim): `runbook:181-206 ($-values, WINDOW_CUSTODY_ROOT/BACKUP_DEST naming, FROZEN_PLAN=custody reservation JSON) and runbook:971 (REPO=${MEASUREMENT_REPO:-…}) vs joulewise/arm_readiness_evidence_t0.py:571-593,652-676,1138-1156`
- failure_scenario (verbatim):
  > A freeze-step that copies the runbook's own example produces window.env with $-containing values (parser refuses as ambiguous), missing CUSTODY_ROOT/CLAIM_BACKUP_DEST/BOUND_BACKUP_DEST keys, a FROZEN_PLAN that is not the pack's calibration_plan.json (E-8 capture argv then fails the reviewed-literal check), and a chain whose REPO line fails the exact-binding regex — four independent guaranteed authoring refusals discovered only at night
- Seat report: §4 B6 (`:105`).
- **Refuter disposition:** CONFIRMED both lenses, **plus a NEW production-only defect found by the contract lens**: "author line 1149 joins plan_tree.json's repo-relative plan path onto pack_root → doubled nonexistent path…; **test fixture uses bare filename so suite misses it**. FROZEN_PLAN meaning needs a ruling before changing prose or parser." (`refuter-verdicts.md:74-77`; probe V6 observed `author_expected_exists= False` / `actual_exists= True`). That ruling became **Phase 0 R2** (`council-verdict.md:75`).

### F7 [blocker] Launch without arm/consume ceremony is not machine-caught at launch or by any downstream consumer
- `file_line` (verbatim): `runbook:964-1148 (window-chain.zsh performs no receipt check); grep: arm_readiness.consumptions referenced only in joulewise/arm_readiness.py and arm_readiness_evidence_t0.py`
- failure_scenario (verbatim):
  > Ed (or a rushed magistrate) skips E-9a/b/c after the E-9 reservation and runs the launch recipe: the chain settles, calibrates and collects a normal-looking window with no refusal anywhere; the only gate on the missing arm/consumption lineage is human close-out item 5 — the required launch-license output neither traces through a machine consumer nor fails closed (cross-confirm consumer side with L5/L6/L7/L10)
- Seat report: §4 B7 (`:106`); matrix cell **E = N** (`:74`) — the seat's only true fail-open.
- **Refuter disposition:** CONFIRMED blocker by both DG lenses. Contract lens: "consume_launch_capability exists but never execs; chain has no receipt check; zero downstream consumers authenticate launch lineage" (`refuter-verdicts.md:42-44`). Execution lens: "a skipped manual step can spend the entire quiet window normally. **The minimal remedy is an executable launch admission boundary—not another checklist**… A single launcher should consume/revalidate the capability and immediately `exec` the chain, while direct chain invocation without the bound consumption context refuses before the first settle."
- **RULED CONTRACT-BEARING** at Phase 0: `council-verdict.md:78` — "L8-B7 launcher binding is contract-bearing (Opus W7)."

### F8 [should_fix] Arm CLI demands the ARM_CONTEXT JSON inline while the authenticated arm-context.json already sits in custody
- `file_line` (verbatim): `scripts/generate_arm_readiness.py:58-70; runbook:834-848`
- failure_scenario (verbatim):
  > Inside the 20-minute volatile fuse Ed must supply a ~700-character exact-key JSON object on the command line; any drift from the t0.inputs arm-context breaks cross-binding, and the obvious workaround `--arm-context "$(cat …)"` is nowhere documented — accept the custody path or freeze the cat-substitution literal in the packet
- Seat report: §4 S1 (`:109`). No refuter assigned.

### F9 [should_fix] The 5-minute arm-receipt validity fuse is documented nowhere the operator can see
- `file_line` (verbatim): `joulewise/arm_readiness.py:3596 (validity_ns=300_000_000_000), :3952-3955; absent from runbook §5C and the packet`
- failure_scenario (verbatim):
  > Ed pauses six minutes between E-9a and E-9c to phone the magistrate with the receipt sha; verify/consume refuse readiness_record_expired; nothing tells him a re-arm inside the surviving 20-minute evidence horizon is the licensed recovery, so the night ends on a recoverable refusal
- Seat report: §4 S2 (`:110`); matrix cell **Q** (`:86`) — "fuse documented **nowhere** operator-visible". No refuter assigned.

### F10 [should_fix] Re-author cleanup is a raw rm -r on custody paths with no shape verification
- `file_line` (verbatim): `runbook:823-827`
- failure_scenario (verbatim):
  > At 2am after a reboot, a mistyped $PACK_ID that resolves to a sibling pack's custody removes that pack's T-0 namespaces irreversibly with no confirmation and no receipt; the only guard is the prose instruction to 'first verify' (executed: the unset-vars variant is harmless, the wrong-existing-path variant has no catch)
- Seat report: §4 S3 (`:111`); matrix cell **S = N** (`:88`); executed falsifier F6 (`:57`). No refuter assigned.

### F11 [should_fix] Morning restore (E-16) before the magistrate finishes has no machine catch
- `file_line` (verbatim): `runbook:557-568; packet §3.5`
- failure_scenario (verbatim):
  > Ed restores network time at tap 2 before the magistrate reports verdict+margin+backups complete; systemsetup succeeds silently, the wall clock may slew under the still-running clock-anchored close-out reads, and only honestly-recorded §12 item-20 timestamps could ever reveal it — the two-tap gap is purely procedural
- Seat report: §4 S4 (`:112`); matrix cell **T = N** (`:89`). No refuter assigned.

### F12 [should_fix] In-horizon TOCTOU: post-authoring process starts are not re-probed at arm/verify/consume
- `file_line` (verbatim): `joulewise/arm_readiness_evidence_t0.py:47 (design comment); verify/consume re-check only horizon+boot+roots`
- failure_scenario (verbatim):
  > Ed starts a browser 'just to check the time' after authoring; all receipts stay valid for the remaining horizon and ARM/consume pass; the bounded 20-minute window is a deliberate design trade but the runbook's prohibition ('do not start any new … process') has no teeth inside it — the recut packet must carry the prohibition as an explicit ABORT row
- Seat report: §4 S5 (`:113`); matrix cell **R = N (bounded)** (`:87`). No refuter assigned.

### F13 [nit] prewindow check 8's agent pattern omits claude/t3 and check 4 WARN-only without admin
- `file_line` (verbatim): `scripts/prewindow_check.sh:102-110,155`
- failure_scenario (verbatim):
  > Executed: check 8 printed OK while this live Claude session ran; between E-7b and authoring, only prewindow guards the machine and it cannot see a forgotten claude/t3 process (the T-0 census later catches it)
- Seat report: §4 N1 (`:116`); executed falsifier F7 (`:58`). No refuter assigned.

### F14 [nit] E-14 do-not-return-before time is hand arithmetic at T-0
- `file_line` (verbatim): `packet §3.4 E-14; plan 6.28 h = 6 h 16.8 m`
- failure_scenario (verbatim):
  > A 2am mental addition of 6.28 h invites an early return; the recut packet should carry a `date -v+377M` literal
- Seat report: §4 N2 (`:117`). No refuter assigned.

### F15 [nit] ED-session census pattern is substring-based and false-positive-prone (fails closed)
- `file_line` (verbatim): `scripts/ed_session/rail-probe.sh:48, sampler-checklist.sh:44`
- failure_scenario (verbatim):
  > Executed: any process whose argv merely contains 'powermetrics' (test fixtures, a plist path) refuses the qualification run; harmless for soundness but a qualification session run beside any dev activity will refuse spuriously
- Seat report: §4 N3 (`:118`); executed falsifier F5, organic (`:56`). No refuter assigned.

### The seat's eight work orders (verbatim, `raw/L8-triage.md:74-88`) — mapped for §2

WO-L8-1 capture wrapper + §5C rewrite (F1) · WO-L8-2 prewindow min-idle floor + re-frozen literal
(F2) · WO-L8-3 clock-probe privilege route + rehearsal (F3, ED-Q-L8-1) · WO-L8-4 re-freeze pack +
M-2 ruling (F4, struck) · WO-L8-5 recut FINAL packet (F5, F8, F9, F12, F14) · WO-L8-6 §4/§6
template alignment (F6) · WO-L8-7 machine-enforce the launch license (F7) · WO-L8-8 governed
`reauthor-clean` (F10).

---

## 2. WHAT CHANGED SINCE 2026-08-15

Council-side execution vehicles located: **WO-T0-PRODUCER** (PR **#152**, merge `a61ac92`,
TASK_QUEUE Completed row line **108**), **#154 T-0 F4 honest contract** (merge `a59c795`, commits
`65cc0f3` → `d8d2022` → `32cf987`), **WO-LAUNCH-BINDING** (PRs **#156** `f392ff6` and **#157**
`bd333de`; still open as queue row **A1**, TASK_QUEUE line **536**), **WO-KERNEL-RECONCILE** (#150
`47d2645`), the **D-127 sudoers install** (Ed, 2026-08-17 evening), the **dress-rehearsal builder +
operator card** (`ad14ac4`), and the **D-149** automation surface (`0e96dbb`, `79a4cd0`, `b92b43d`
— all **branch-only**).

### F1 — **FULLY ADDRESSED as a producer; the authenticity residual is now an ACCEPTED REGISTERED LIMITATION, not a closed defect**
- `scripts/capture_t0_step.py` **exists and is on main** — `a61ac92` "WO-T0-PRODUCER: T-0
  acquisition capture tool + R2 resolver + D-127 clock route + dwell/env hardening (#152)".
  It emits the six step captures plus `clock-attestation.json`, `arm-context.json`,
  `launch-manifest.json` into the private input namespace (step→filename map at
  `scripts/capture_t0_step.py:55-70`; attestation writer at `:536-598`).
- **Runbook §5C rewritten** to the wrapper flow: E-4…E-9a are now `capture_t0_step.py <step>`
  invocations (`docs/phase_2/window_runbook.md:908-967`), with the closing guarantee at `:969-972`:
  "After E-9a, the private input namespace contains exactly the six captures plus
  `clock-attestation.json`, `arm-context.json`, and `launch-manifest.json`."
- **Terminal-review trailer producer** (the ADDENDUM's added obligation) landed as an operator step,
  not a tool: the rehearsal card §2 (`docs/process/rehearsal-operator-card.md:25-31`) has Ed create
  the empty `JouleWise-Terminal-Review: PASS` / `-Tree-Oid` / `-Pack-Sha256` commit by hand.
- **The forgery hazard was NOT engineered away — it was reclassified.** `#154` (`a59c795`,
  commits `65cc0f3`/`d8d2022`/`32cf987`) "supersedes the D-134 cl.6 overclaim (production-interface/
  ceremony rule, **no operator-fabrication-resistance claim**), registers the TRUSTED-OPERATOR
  limitation v1, and removes the public execute/monotonic_ns/utc_now injection seam from
  `capture_t0_step`". Live text: `scripts/capture_t0_step.py:4-10` — "The production CLI is a
  trusted-operator ceremony interface, not independent … deliberate operator fabrication."
  **D-148 ruling 6** (decision_log `:171`) then ACCEPTED the whole family — "recorder race / T-0
  capture provenance / hostile same-UID injection / forged launch-context … **ACCEPTED AS
  REGISTERED LIMITATIONS** — in-process adversary out of model, per D-139 A1."
- WHERE: main (`a61ac92`, `a59c795`).
- NOT DONE: no human has executed the wrapper end-to-end (see ED-Q-L8-2).

### F2 — **FULLY ADDRESSED in code; never exercised live**
- `scripts/prewindow_check.sh:37` now reads `MIN_CLEAN_DWELL_S=600 # continuous clean time required
  by D-134`, and `:172-199` implements exactly the refuter's ruled remedy: a `clean_since` monotonic
  interval, reset to `-1` on **any** failed sample, with the comment "three quick samples are not a
  substitute for the idle dwell that D-134's T-0 author independently checks."
- Runbook `:937-939`: "**E-7b:** capture the profile-derived `--wait --timeout-min 45` command.
  The script must prove at least 600 seconds of continuous clean dwell and end in `READY`."
- The author's own 600-s threshold was **not** lowered (the refuter's explicit instruction).
- WHERE: main (`a61ac92`; later touched by `b6553fd`).
- NOT DONE: no recorded 600-second live dwell. The rehearsal card marks E-7b **ED-FIRST**
  (`rehearsal-operator-card.md:13`, §7 `:69-75`).

### F3 — **FULLY ADDRESSED: the privileged route was re-shaped, and the grant is installed and ground-truth verified**
- **The probe changed.** `joulewise/arm_readiness_evidence_t0.py:891-916` (`_derive_clock_probe`)
  now issues a fresh `("/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-setusingnetworktime",
  "off")` — the **D-127-granted write vector** — and refuses only if that enforcement fails. The
  ungranted `-getusingnetworktime` read is gone from the authoring path; the prior-state read is now
  **interactive** (`scripts/capture_t0_step.py:605-606`, `INTERACTIVE_PRIOR_STATE_ARGV`; rehearsal
  card §4: "the password prompt is normal").
- **The sudoers slice is installed.** Runbook `:556`: `Cmnd_Alias JOULEWISE_NETWORK_TIME =
  /usr/sbin/systemsetup -setusingnetworktime off, /usr/sbin/systemsetup -setusingnetworktime on`;
  runbook `:547` "the capture wrapper and the T-0 author use the `off` vector, and restore uses…".
  Install evidence: `docs/run_reports/2026-08-18-t10-session.md:104` — "Installed root:wheel 0440;
  digest **`7dfe980b…`** verified; **both** vectors passwordless with ground-truth state flips".
  Primary custody read directly: `~/JouleWise-window-custody/ed-qual-20260817/sudoers-digest.txt`
  = `7dfe980be89a7912d69c6e72b5582649fc4c50db88bf709bcfbb4a1c34e4406d
  scripts/joulewise-network-time.sudoers`; `sudoers-vector-{on,off}.txt` show
  `setUsingNetworkTime: On` / `Off`; `vector-{on,off}-confirmed.txt` show `Network Time: On` /
  `Network Time: Off`; `clock-{prior,post}-state.txt` both `Network Time: On`.
- WHERE: code on main (`a61ac92`); install is machine state, evidenced off-repo in custody.

### F4 — **STRUCK at the sitting; the underlying pack world has since changed twice**
- Nothing to repair (Disposition 4). Recorded for the seat's situational awareness only:
  - `_v2` family + **freeze-0002** minted 2026-08-18 in the measurement checkout
    (`docs/process/ed-morning-packet-2026-08-18.md:11-14`, exact-byte table at `:93-97`).
  - **D-147** then replaced that with the **`_v3`** family + **freeze-0003**
    (`docs/decision_log.md:171` D-147 row). Receipts exist on the branch:
    `configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json`
    (+ `.sha256`); commits `5e38f1e`, `eb7f6c6`, `94dc3b3` — **branch-only, not on main**.
  - **M-2** (the struck finding's second clause): the remanded cold gate **ran** —
    `docs/process_traces/2026-08-15-m2-coldgate/` holds `packet.md`,
    `coldgate-adjudicator-ruling.md`, `coldgate-opus-refuter-findings.md`, `composed-verdict.md`.
    **D-140** then ruled freeze-status byte semantics ("Receipts govern over descriptive bytes for
    ALL successor packs… remaining descriptive bytes are never repaired", decision_log `:8872-8886`).
    The runsheet's step 8 carries "the M-2(b) informational operator note **into the successor
    packet** before the arm gate" (`docs/process/phase2-transaction-runsheet.md:103-111`) — and that
    successor packet does not exist (see F5).

### F5 — **NOTHING CHANGED for the packet itself; the artifact that would replace it has not been created, and its nearest substitute is already stale**
- The FINAL arm packet is still the only arm packet, unmodified, at
  `~/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md`
  (directory listed; also present: `arm-packet-alpha-SKELETON.md`,
  `arm-packet-discrepancy-resolutions.md`). **No successor/recut packet was located** — searched
  `grep -rln "arm-packet" docs/`, which returns only historical run reports, the council directory
  and the decision/council logs; `docs/process/` contains no packet file.
- Council order places it late by design: "then the successor arm packet ONLY after the T-0 repair
  passes end-to-end at the exact reviewed head (Opus W8)" (`council-verdict.md:99-100`); the runsheet
  likewise says "The successor packet carries exactly one informational note…" (`:103`) as future work.
- What DOES exist, and is a **different artifact class**:
  - `docs/process/rehearsal-operator-card.md` (`ad14ac4`, on main) — a **rehearsal** card, not the
    night packet. It carries the missing content the finding named (T-0 author step §10, the bolded
    20-MINUTE horizon `:95`, the `$(cat …/arm-context.json)` literal `:104`, E-10 sole launcher
    `:110`, restore + reset `:115-122`). **But it is stale at the current head**: it binds
    `d117_floor_qwen25_1p5b_v2`, freeze-**0002**, and the measurement checkout
    `/Users/edr/JouleWise-measurement-20260818` (`:3`, `:20`, `:30`), while the live family is `_v3`
    with freeze-**0003**.
  - `docs/process/window-run-cards/shakedown-v3-first-light.md` (`b92b43d`, **branch-only**) and
    `docs/process/d149-go-receipt-template.md` (`79a4cd0`, **branch-only**) — the D-149 lane, below.

### F6 — **LARGELY ADDRESSED; residual is family-staleness, not contract violation**
- `window.env` example (`docs/phase_2/window_runbook.md:188-212`) is now literal-valued (no `$`),
  and carries `CUSTODY_ROOT`, `CLAIM_BACKUP_DEST`, `BOUND_BACKUP_DEST` as separate keys, with
  `FROZEN_PLAN=/…/d117_floor_qwen25_1p5b_v2/calibration_plan.json` — the pack's plan, as the deriver
  requires. Explanatory prose added at `:220-232`, including "`CUSTODY_ROOT` and
  `WINDOW_CUSTODY_ROOT` are deliberately the same literal: the former is the T-0 producer/author
  contract key…".
- Chain `REPO=` is now the bare literal at `:1150` and `:1201`
  (`REPO=/Users/edr/JouleWise-measurement-20260813`) — the `${MEASUREMENT_REPO:-…}` fallback is gone.
- Doubled plan-path: the **strict R2 plan resolver** shipped with `a61ac92`; runbook `:233-237`
  records the ruling's consequence — "The v1 ALPHA and BETA `plan_tree.json` bytes carry the
  superseded repository-relative spelling; the shared R2 resolver refuses those packs, and they are
  never basename-repaired in an operator file." (The R2 ruling is Phase 0 R2 →
  `docs/process_traces/2026-08-15-r2-frozen-plan-consult/`, then D-147.)
- **RESIDUAL:** the example binds the **`_v2`** family and `MEASUREMENT_REPO=…-20260813`
  (`:189`, last touched by `844453a` "window.env example flipped whole to the _v2 family"), while
  the live family is **`_v3`** and the designated measurement checkout in the rehearsal card is
  `…-20260818`. WO-L8-6's alternative remedy ("or generate them mechanically from the pack") was not
  taken — the templates are still hand-maintained prose.
- WHERE: main.

### F7 — **SUBSTANTIALLY ADDRESSED and CONTRACT-RULED; the work order is STILL OPEN and the runbook itself says this is not launch authority**
- **Contract first** (as Phase 0 required): `docs/process_traces/2026-08-15-launch-f3-consult/` →
  `docs/process_traces/2026-08-16-launch-f3-coldgate/` (`14-composed-verdict.md` is the ONE home;
  `docs/run_reports/2026-08-16-t9-session.md:59-60, 218-234`), plus the
  "**D-134/D-137 launcher-binding amendment — 2026-08-15**" block at `docs/decision_log.md:9453`.
- **Code:** `scripts/launch_window.py` — "Atomically consume, revalidate, and exec one frozen D-117
  window" (`:2`), calling `verify_consumed_launch` at `:235` and `:257`. Merged via **#156**
  (`f392ff6`) and **#157** (`bd333de`), **both on main**. Fix round 2 (`66884c6`) **deleted** the
  public consumption wrapper and both caller-frame guards ("forgeable checks must not exist even as
  decoration"), leaving "atomic no-clobber primary = the only real enforcement".
- **Runbook:** E-10 is now the sole route (`:1055-1078`) — one invocation "generates the
  anonymous-FD handoff, atomically creates and fsyncs the no-clobber consumption primary (the
  single-use linearization point), publishes its sidecar, replays `verify_consumed_launch`, and
  calls `execve` on the exact frozen foreground argv"; "Standalone `consume`, direct
  `window-chain.zsh`, and direct stage invocations are not production routes"; the retained
  `consume` CLI "now refuses with registered `readiness_usage_invalid`". Downstream refusal rows
  added to §10: `launch_consumption_missing`, `launch_binding_mismatch`, `launch_lineage_conflict`,
  `launch_handoff_invalid` (`:1612-1617`).
- **STILL OPEN, stated by the repo itself.** Queue row **A1 `WO-LAUNCH-BINDING` — READY [AGENT]**
  (TASK_QUEUE `:536`): "Note: Stages 1-3 MERGED (#156 f392ff6, #157 bd333de); calibration-side stage
  2 DONE on the staged estimator branch @ e22e658 (delta-ACCEPTED, rides the re-freeze per the
  Phase-2 plan); **remaining: stage 4 successor flag inside the transaction. Launch stays NO-GO**."
  Runbook `:1079-1090`: "**Current implementation boundary (2026-08-15 fix round):** … Calibration-slot
  writer enforcement is not implemented yet… Therefore this E-10 command is a documented target
  procedure, **not current authority to launch**: every D-117 physical launch remains NO-GO until
  those gates and the full review gauntlet close."
- **Accepted residual:** in-process same-UID forged launch context — D-148 ruling 6.

### F8 — **NOTHING CHANGED in the CLI; one of the two offered remedies exists only in the rehearsal card**
- `scripts/generate_arm_readiness.py:47` still `arm.add_argument("--arm-context", required=True)`,
  and `:61-65` still refuses a path: `"--arm-context must be the JSON object itself, not a path"`.
  Runbook `:1034` repeats it verbatim: "`ARM_CONTEXT_JSON` is the exact JSON object itself, not a path."
- The seat's second remedy ("freeze the cat-substitution literal in the packet") **is** realised —
  but in the rehearsal card, `docs/process/rehearsal-operator-card.md:104`:
  `--arm-context "$(/bin/cat …/arm_readiness.t0.inputs/arm-context.json)"`. There is no night packet
  to carry it (F5).

### F9 — **NOTHING CHANGED (NO-REPAIR-FOUND)**
- The fuse still exists: `joulewise/arm_readiness.py:6101` `validity_ns: int = 300_000_000_000`
  (the file grew; the seat cited `:3596` at baseline).
- It is still operator-invisible. Searched: `grep -n "validity\|300 seconds\|five minutes\|5 minutes"
  docs/phase_2/window_runbook.md` → **no matches**; `grep -rn "300_000_000_000\|five-minute\|5-minute"
  docs/` → only the council record, unrelated 5-minute caps in
  `docs/contracts/measurement_methodology.md:293` / `docs/phase_2/phase_2_plan.md:389,673`, and the
  rail-probe reference in `docs/council_log.md:3620`. The licensed recovery (re-arm inside the
  surviving 20-minute horizon) is likewise undocumented in operator surfaces.

### F10 — **NOTHING CHANGED (NO-REPAIR-FOUND); the exposure grew from two namespaces to three**
- Runbook `:1011-1021` still: "Before re-authoring, first verify these are the exact three
  pack-specific T-0 namespaces and remove all three so no no-clobber collision can masquerade as a
  retry: `/bin/rm -r -- "$ARM_READINESS_CUSTODY_ROOT/$PACK_ID/arm_readiness.t0.sources"
  "…/arm_readiness.evidence" "…/arm_readiness.t0.inputs"`". Guard is still the prose "first verify".
- No governed operation exists. Searched: `grep -rn "reauthor" scripts/ joulewise/ docs/` → hits
  only the council record (`triage.json:595`, the seat report). No `reauthor-clean` subcommand in
  `scripts/generate_arm_readiness.py` or `scripts/capture_t0_step.py`.
- The rehearsal card §11 (`:122`) reproduces the same raw `rm -r` with three fully-expanded literals.

### F11 — **PARTIALLY ADDRESSED (documentation only; still no machine catch)**
- Runbook `:627-637` now orders the restore explicitly last, with rationale: "The restore comes last
  because re-enabling automatic network time permits… confirm `measurement_complete`, then hand back
  — the restore…", and `:637` / `:1828` require recording "when [network time] was disabled, and
  when it was restored (§5A)".
- No mechanical enforcement was located: the ordering remains procedural, exactly as the finding
  states. The old E-16 label no longer appears (`grep -n "E-16" docs/phase_2/window_runbook.md` →
  no matches); the E-numbering was renumbered by the T9 merge resolution
  (`docs/run_reports/2026-08-16-t9-session.md:111`), so the seat should re-locate the row by content.

### F12 — **PARTIALLY ADDRESSED (prohibition now prominent; still no re-probe)**
- Runbook `:1003-1009` makes the horizon the operator's visible clock: "Eleven volatile evidence
  kinds carry a **20-minute monotonic horizon** beginning at E-9b. That is the operator's visible
  clock: **do not start any new agent, browser, `caffeinate`, monitor, maintenance, or other polling
  process after authoring.** Run ARM immediately, verify it, stop for Ed's inspection, and then
  invoke E-10." Rehearsal card `:95` carries the same in bold.
- **The teeth are still absent.** The census probes are authoring-time only:
  `joulewise/arm_readiness_evidence_t0.py:1384-1397` (`_derive_process_census`) runs four fresh
  `pgrep` probes at derivation; `scripts/launch_window.py` re-checks consumption/binding
  (`verify_consumed_launch`) but no process census — `grep -n "census" scripts/launch_window.py` →
  no matches. No ABORT row exists because no packet exists (F5).

### F13 — **PARTIALLY ADDRESSED: check 4 restructured; the agent pattern is unchanged**
- Check 4 no longer WARNs: `scripts/prewindow_check.sh:101-104` now reads "Clock state is
  deliberately not read here. D-127 grants repository automation only the exact off/on writes; Ed
  records the prior state in interactive E-4 and E-5 performs the governed exact off enforcement",
  emitting a NOTE. The admin-dependent WARN path is gone.
- **The agent pattern still omits claude/t3**: `:148-150` —
  `procs="$(ps aux | grep -E "codex exec|codex-run|run_campaign|window-chain" | grep -vc grep)"`.
  The T-0 author's own census does cover them
  (`arm_readiness_evidence_t0.py:1388`: `("/usr/bin/pgrep", "-lf", "codex|claude|t3")`), which is
  exactly the compensating layer the finding already credited.

### F14 — **NOTHING CHANGED (NO-REPAIR-FOUND)**
- E-14 lives only in the un-recut off-repo packet. Searched: `grep -rn "E-14" docs/` → only
  `triage.json:592,692-693`, `sitting-packet-FINAL.md:167`, and the seat report. `grep -n "date -v"
  docs/phase_2/window_runbook.md docs/process/*.md` → no matches. No `date(1)` literal was frozen anywhere.

### F15 — **NOTHING CHANGED in the scripts; the over-match is now confirmed ground truth**
- `scripts/ed_session/sampler-checklist.sh:43` and the matching block in `rail-probe.sh:48-54` still
  use `/usr/bin/pgrep -fl '[p]owermetrics'` and refuse on rc 0 ("REFUSE: a powermetrics process
  already exists."). Fail-closed, unchanged.
- New evidence: the 2026-08-17 quiet census "**the L8/L9 over-match findings confirmed as fixture
  ground truth**" (`docs/run_reports/2026-08-18-t10-session.md:109`; custody
  `~/JouleWise-window-custody/ed-qual-20260817/quiet-census/` — 7 files incl. `census-agent.txt`,
  `census-browser.txt`, `census-monitor.txt`, `CAPTURE-NOTE.txt`).
- The related repair, **A4 `WO-CENSUS-SEMANTICS`**, is still **BLOCKED — ED-Q-L9-3** in the generated
  queue (TASK_QUEUE `:538`, `:632`) even though ED-Q-L9-3's fixture was captured 2026-08-17. Either
  the kernel row is stale or the row's precondition is read more strictly than the capture satisfies.

### Cross-cutting: the seat's SIX UNEXECUTED OBLIGATIONS (`raw/L8-triage.md:100-112`)

| Obligation (abridged; verbatim in §1 source) | State at this head |
|---|---|
| `quiet_mac_prep.sh` live execution | **STILL UNEXECUTED.** It is now wrapped as E-7a (`capture_t0_step.py:615-616` → `("/bin/bash", …/scripts/quiet_mac_prep.sh)`), and the rehearsal card marks E-7a **ED-FIRST** (`:13, :61-67`). Searched `grep -rn "quiet_mac_prep" docs/run_reports/ docs/process/ RUN_STATE.md docs/phase_2/` — no live-run record after 2026-07-17. |
| Live sudo paths of `rail-probe.sh` / `sampler-checklist.sh` | **EXECUTED 2026-08-17** — see ED-Q-L8-3. |
| E-9 reservation double-reserve / live-writer behavior vs a ledger copy | **NOT located as executed.** The rehearsal card documents a hard stop before it (§8, `calibration_ledger_head_uncommitted`). L2 remains primary owner. |
| Runbook §10 refusal-row completeness for the 2am operator | **NOT audited row-by-row by anyone located.** §10 grew (four new `launch_*` rows, `:1612-1617`), which enlarges rather than discharges the obligation. Packet O-9's one-page extract still does not exist (no packet). |
| Morning §9/§11 magistrate procedures | Out of this seat's scope (L10). |
| Real custody artifacts in `~/JouleWise-window-custody` | Read read-only for this row; contents enumerated in §3. |

### D-149 effect on the operator model

**What D-149 says** (`docs/decision_log.md:172`, adopted 2026-08-19 night by Ed; body at `:8865-8870`;
commit `0e96dbb` — **branch-only, not on main**): for any quiet-Mac window needing **no physical
presence**, T-0 GO is **AUTO-ISSUED** when five conditions hold, "evaluated mechanically at T-0 and
written into the window's custody record as a GO receipt": (1) a READY-candidate council verdict
stands; (2) the arm ceremony passes every gate with freshness horizons honored; (3) the machine is
quiet; (4) boot-session and clock-discipline checks pass; (5) D-078 no-retry binds. "**REMAINS ED'S:
anything needing hands (cables, backlight, reboots, new sudo), claim publication, exact-byte
confirmation.**" It "**Supersedes the per-window 'separate perishable T-0 GO from Ed' fence for
no-hands windows**". The kernel fences for D117-W-ALPHA/BETA/GAMMA were updated in that commit
(TASK_QUEUE `:537` etc.: "T-0 GO auto-issues per D-149 when its five recorded conditions pass").
D-148 ruling 4 is its companion: "**QUIET WINDOWS ARE LEAD-DELEGATED**" (`decision_log.md:171`).

**Per-finding effect** (this is the seat's call to make; the mapping below is assembled, not ruled):

| Finding | D-149 effect |
|---|---|
| F1 producer | **UNTOUCHED, and arguably sharpened.** D-149 removes the operator from the loop but the wrapper still needs a human for the two registered irreducible observations (the trusted-clock UTC literal and the pasted prior-state line, `capture_t0_step.py:8`, `:43`) and for the interactive prior-state read. A no-hands window must therefore either skip or automate exactly the steps the trusted-operator limitation rests on. **No seat has audited that seam.** |
| F2 dwell | Untouched (mechanical). |
| F3 clock privilege | **Re-scoped.** The E-4 prior-state read is interactive (password prompt); D-149 says "new sudo" remains Ed's. Whether an unattended run can perform E-4 at all is unresolved in the located documents. |
| F5 packet | **Re-scoped, possibly replaced.** The operator "tap script" is being displaced by the **run-card + GO-receipt** pair (`window-run-cards/shakedown-v3-first-light.md`, `d149-go-receipt-template.md`). Neither has been through any review gauntlet; both are branch-only. |
| F7 launch license | **In direct tension.** The runbook still requires "**Ed's deliberate physical launch**" at E-10 after a hard stop for personal inspection ("No verdict, author, verifier, or other automated command may cross this boundary", `:1051-1056`), and the A1 fence says "the launcher enforces admission but never becomes physical launch authority; **Ed still launches**" (TASK_QUEUE `:536`). D-149 authorises no-hands windows. **Who invokes `launch_window.py` in a no-hands window is not resolved in any document located.** |
| F9 fuse / F8 arm-context | **Re-scoped away from fatigue, toward automation.** A machine issuer does not mis-type JSON or pause six minutes to phone anyone — but nothing documents the automation's own behaviour at the 5-minute fuse. |
| F11 restore ordering | **Re-scoped.** The two-tap morning gap presupposes taps. Under D-149 the restore becomes an automation step with no stated ordering guard. |
| F12 TOCTOU | **Mitigation possibly REMOVED.** The prohibition's only enforcement was a human reading "do not start any new … process". An unattended loop that wakes to poll is precisely the prohibited class. D-149 condition (3) "no interactive use, single writer" is the replacement, and it is checked **once at T-0**, not inside the horizon. |
| F13 prewindow pattern | **Sharpened.** The prewindow agent pattern that misses `claude`/`t3` is the layer a lead-driven loop would trip; C3's evidence line is "pgrep evidence attached [ ]", with the pattern unspecified in the template. |
| F14 return time | **Mooted for no-hands windows** (nobody returns) — but not formally retired by any ruling located. |

**Has any seat audited the automation itself? NO — none located.** The GO-receipt evaluator is
explicitly deferred: `docs/process/d149-go-receipt-template.md:63-66` — "a mechanical evaluator
script MAY be built to fill C2–C4, but **it goes through the ordinary gauntlet first; until then the
issuer fills the receipt by running the runbook commands and attaching outputs**." The commit
subject says the same: `79a4cd0` "…(prep item 6; **evaluator script deferred to gauntlet**)". So at
this head the "mechanical evaluation" D-149 describes is a **markdown checklist with `[ ]` boxes
filled by the issuing agent**, and the two D-149 artifacts (`79a4cd0`, `b92b43d`) plus D-149 itself
(`0e96dbb`) are **branch-only, unreviewed by any council seat**.

---

## 3. ED-QUALIFICATION ROWS (ED-Q-L8-1 .. ED-Q-L8-4)

All four are **sudo/Ed rows**. Note before reading: the row IDs themselves are **not tracked
anywhere in the live repo** — `grep -rn "ED-Q-L8" --include=*.md --include=*.json .` outside the
council directory returns **zero hits**; the kernel/queue reference ED-QUALIFICATION only
generically ("all ED-QUALIFICATION rows closed with evidence", `state_kernel.json:9`,
TASK_QUEUE `:598`). Closure below is reconstructed from custody and run reports, not from a ledger.

### ED-Q-L8-1 (sudo) — **CLOSED WITH DIRECT PRIMARY EVIDENCE (with one contract caveat)**
> ED-Q-L8-1 (sudo): decide and prove the privileged read path for the T-0 CLOCK_PROBE — either a scoped read-only sudoers entry for `/usr/sbin/systemsetup -getusingnetworktime` or a ratified `sudo -v` warm-up literal immediately before the T-0 author — and exercise it once in a tap block; D-004's powermetrics-only NOPASSWD plus a >10-min-cold sudo timestamp otherwise guarantees an authoring refusal at night

**LOCATED CLOSURE EVIDENCE** (all read directly for this row):
- `~/JouleWise-window-custody/ed-qual-20260817/sudoers-digest.txt` — `7dfe980be89a7912d69c6e72b5582649fc4c50db88bf709bcfbb4a1c34e4406d  scripts/joulewise-network-time.sudoers`.
- `sudoers-vector-off.txt` / `sudoers-vector-on.txt` — timestamped **2026-08-17 17:56:53** PT,
  `setUsingNetworkTime: Off` / `On` (both carry the benign macOS `### Error:-99 … InternetServices.m`
  line that `systemsetup` always prints).
- `vector-off-confirmed.txt` = `Network Time: Off`; `vector-on-confirmed.txt` = `Network Time: On`
  — the **ground-truth state flip**, i.e. live sudo genuinely ran.
- `clock-prior-state.txt` (17:47) and `clock-post-state.txt` (17:57) both `Network Time: On` — the
  machine was left restored.
- Corroboration: `docs/run_reports/2026-08-18-t10-session.md:104` (row table) and `:9-10`
  ("Ed at the machine, ~17:40–22:05 PT"); `docs/process/ed-morning-packet-2026-08-18.md:113`.
- Machine: Ed's M3 Max MBP (the T10 report's session machine). Date: **2026-08-17 PT** (the report
  and the dir name use the PT-completion convention; the report's title says 2026-08-17/18).
- Durable receipt: yes — five custody files, plus the tracked sudoers file whose digest they pin.

**CAVEAT the seat should weigh:** the row asked to prove a **read** path
(`-getusingnetworktime`) or ratify a `sudo -v` warm-up. **Neither was done.** The defect was instead
dissolved by changing the contract: the author now probes the **write** vector
(`-setusingnetworktime off`, `arm_readiness_evidence_t0.py:900-905`) and the prior-state **read** is
performed **interactively with a password prompt** (`capture_t0_step.py:605`, rehearsal card `:43-47`
"the password prompt is normal"). What was exercised is the installed write grant. Whether an
interactive password prompt at E-4 is acceptable — especially under D-149's no-hands model — is a
live question, not a closed one.

### ED-Q-L8-2 (sudo + Ed) — **NOT CLOSED. A BUILDER AND A CARD EXIST; THE REHEARSAL WAS NEVER EXECUTED.**
> ED-Q-L8-2 (sudo + Ed): full arm-sequence dress rehearsal on the recut packet — E-4→E-9 under the capture wrapper, T-0 authoring, arm→verify→consume against scratch custody/synthetic roots, with a real ≥10-minute prewindow wait — timed against the 20-minute volatile horizon and 5-minute arm-receipt fuse

The verdict calls this "**the program's most valuable Ed hour**" (`council-verdict.md:91`). The
distinction the task demands — *built* vs *executed* — resolves cleanly and negatively.

**WHAT WAS BUILT (on main, `ad14ac4`, 2026-08-18, "Dress-rehearsal builder + operator card (terra
rounds 1-5)"):**
- `scripts/ed_session/build_rehearsal_env.sh` (10,201 bytes) — builds the scratch custody topology.
- `docs/process/rehearsal-operator-card.md` (123 lines) — eleven sections, paste-ready commands.
- Design record: `docs/process_traces/2026-08-18-t10-t11-working-notes/rehearsal-builder-brief.md`
  (15,842 bytes) and `shakedown-driver.sh`.

**WHAT THE CARD ITSELF SAYS ABOUT EXECUTION** (`docs/process/rehearsal-operator-card.md:7-16`) —
this is the card's own status table, not an inference:

| Step | level |
|---|---|
| Build | BOUNDARY-PROVEN (syntax and reuse refusal smoke; sandbox cannot create the measurement-checkout `.venv`) |
| Part A dry-run | BOUNDARY-PROVEN (requires Ed's terminal-review commit first) |
| E-4 | BOUNDARY-PROVEN (sandbox boot-ID boundary) |
| E-5 | BOUNDARY-PROVEN (no sudo or clock change in smoke) |
| E-7a/E-7b | ED-FIRST |
| E-8 | BOUNDARY-PROVEN (`calibration_ledger_head_uncommitted` for the scratch-ledger route) |
| E-9a/E-9b/ARM/verify/E-10 | ED-FIRST, blocked unless a lead-approved committed scratch-ledger route is supplied |

"BOUNDARY-PROVEN" = an agent reached a sandbox refusal boundary. "ED-FIRST" = **nobody has run it**.

**NO CLOSURE EVIDENCE LOCATED — searched:**
- `ls ~/JouleWise-window-custody/` → 19 entries; **no rehearsal directory**. The card's own scratch
  root, `~/JouleWise-window-custody/ed-qual-20260817/rehearsal` (card `:20`), returns
  `ls: … No such file or directory`. **The builder was never run.**
- `~/JouleWise-window-custody/ed-qual-20260817/` → 15 entries, all timestamped 2026-08-17
  17:46–23:51: sudoers/clock vectors, `ed-session-evidence/`, `keyboard-backlight.txt`,
  `decisive-replay.log`, `quiet-census/`, `rail-probe-load-note.txt`. **No T-0 inputs namespace, no
  arm receipt, no consumption receipt, no prewindow dwell log.**
- `docs/run_reports/2026-08-18-t10-session.md:110` — "| **Dress rehearsal** | **OPEN** — gated on the
  frozen `_v2` alpha pack, i.e. on Ed's item-1 ruling | morning packet §4 |"; `:82` — the REHEARSAL
  stream produced "two NEEDS_RULING returns; held for the frozen `_v2` alpha pack".
- `docs/process/ed-morning-packet-2026-08-18.md:126` — "**OPEN: the dress rehearsal (item 4) only.**"
- `docs/run_reports/2026-08-19-t12-t13-session.md` — `grep -n "rehearsal"` → **no matches**. The
  most recent session did not touch it.
- `RUN_STATE.md` — `grep -n "rehearsal"` → `:458`, `:543`, `:622`, all in **ED-OWED** lists.

**ADDITIONAL DEGRADATION SINCE THE CARD WAS WRITTEN.** The card binds
`d117_floor_qwen25_1p5b_v2`, freeze-**0002**, and `/Users/edr/JouleWise-measurement-20260818`
(`:3`, `:20`, `:30`, and every command block). D-147 has since made the live family `_v3` with
freeze-**0003** (`configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json`,
branch-only). **The rehearsal card is now stale in exactly the way F5 says the FINAL packet is
stale** — a fatigued operator following it would arm against a superseded pack family.

**AND IT CANNOT REACH THE ROW'S SCOPE AS WRITTEN.** The row requires `arm→verify→consume`. The card
documents a hard stop two steps earlier: §8 (`:79`) — "the current production readiness code then
returns `calibration_ledger_head_uncommitted`: it requires the ledger bytes at their selected path
to be committed, while the scratch path necessarily is not. Preserve that refusal and **stop Part B
here**… A lead-approved committed scratch-ledger route is required before E-9a and later steps can
be rehearsed." **That route does not exist at this head** (no ruling located; `grep -rn "scratch-ledger"`
finds it only in the card and the builder brief). So even a perfectly executed rehearsal today would
close E-4…E-8 and leave E-9a→E-10 — the arm/verify/consume half, and the entire 20-minute-horizon and
5-minute-fuse timing the row exists to measure — untested.

### ED-Q-L8-3 (sudo) — **CLOSED WITH DIRECT PRIMARY EVIDENCE (partial on one clause)**
> ED-Q-L8-3 (sudo, already chartered as steps 2-3): live sampler-checklist and keyboard-backlight rail-probe executions on a quiet machine (dry-run staging verified in this audit; the live arms and teardown censuses still need sudo)

**LOCATED CLOSURE EVIDENCE:**
- `~/JouleWise-window-custody/ed-qual-20260817/ed-session-evidence/` — `sampler-checklist-20260818T010430Z.log`
  (0 bytes — the aborted first attempt), `…T011634Z.log` (640 B), `…T011840Z.log` (1,015 B),
  `…T011840Z.plist` (**264,911 B** — a real powermetrics capture, so live sudo genuinely ran), and
  `rail-probe-20260818T011943Z/` (a directory of ABBA arms).
- `docs/run_reports/2026-08-18-t10-session.md:105` — "Sampler lifecycle (ED-QUAL step 2) | PASS —
  cadence mean **1.0128 s**, zero orphans"; `:106` — "Rail probe (JW-MET-3) | ABBA executed; **ANE
  delta exactly 0.000000000 J**; cpu delta **−5.7 J** attributed to concurrent replay load +
  charge-termination step. **Documentation-grade**".
- Backlight rows (the row's second half, and the verdict's separate "keyboard-backlight rows" item):
  `~/JouleWise-window-custody/ed-qual-20260817/keyboard-backlight.txt` —
  `backlight_level=0 / auto_adjust=false / inactivity_dim=never / verification=operator_visual /
  checked_at=2026-08-17T18:00:42-0700`.
- Machine: Ed's MBP; date **2026-08-17 PT** (UTC stamps in the filenames read 2026-08-18T01:xx Z).
- Durable receipts: yes — logs, plist, ABBA directory, backlight literals.

**CAVEATS the seat should weigh:** (a) the rail probe ran **under concurrent replay load**
(the decisive replay was running), which the report itself flags — it is documentation-grade only,
and the boundary verdict still rests on code evidence; (b) `rail-probe-load-note.txt` was
"**lead-restored after the operator's own paste overwrote it**" (`:106`) — a custody-integrity
footnote on the one file that explains the anomaly; (c) the row's "teardown censuses" clause is
evidenced only through the checklist's own `pgrep` assertions and the report's "zero orphans" —
no separate teardown census artifact was located.

### ED-Q-L8-4 (sudo) — **NOT CLOSED. NO CLOSURE EVIDENCE LOCATED.**
> ED-Q-L8-4 (sudo): live quiet_mac_prep.sh run to confirm its three OK literals (passwordless powermetrics, displays asleep, screensaver disengaged) match what the T-0 author's _quiet_capture requires verbatim

**NO CLOSURE EVIDENCE LOCATED — searched:**
- `grep -rn "quiet_mac_prep" docs/run_reports/ docs/process/ RUN_STATE.md docs/phase_2/` → only
  `docs/run_reports/2026-07-17-environment-guard.md:30,68,135` (a `bash -n` syntax check, pre-council),
  `docs/run_reports/2026-07-17-window-a-floors.md:309`, `RUN_STATE.md:3634,3778` (both describing the
  known "Graphics FAIL is the known false…" caveat), `docs/phase_2/window_c_operator_checklist.md:196,355`,
  and the runbook's own invocation at `:419`/`:487`. **No post-council live run.**
- `ls ~/JouleWise-window-custody/ed-qual-20260817/` → no quiet-prep artifact. The 2026-08-17
  qualification evening closed sudoers / sampler / rail probe / backlight / decisive replay /
  quiet census; **`quiet_mac_prep.sh` is not among them** (T10 report `:102-110` row table confirms
  the closed set).
- The step now exists as **E-7a** inside the wrapper — `capture_t0_step.py:615-616`
  `("/bin/bash", str(context.repository / "scripts/quiet_mac_prep.sh"))` — and the rehearsal card
  marks E-7a **ED-FIRST** (`:13`, §6 `:61-67`). **So ED-Q-L8-4 is now a strict sub-step of
  ED-Q-L8-2**, and inherits its blockage.
- The row's specific comparison — the three OK literals vs `_quiet_capture`'s verbatim requirements
  — has no located artifact of any kind, executed or desk.

---

## 4. CANDIDATE DISPOSITIONS FOR THE SEAT TO ADJUDICATE

**Candidate dispositions are assembled, not adjudicated; the seat rules.**

| Item | Candidate disposition | What the seat is weighing |
|---|---|---|
| **F1** producer | READY-evidence-attached, **with a reclassification the seat must accept or reject** | `capture_t0_step.py` (main, `a61ac92`) + runbook §5C rewrite close the *missing-tool* defect; the *forgery-indistinguishability* half was NOT engineered away — it was superseded as a claim (`#154`/`a59c795`) and ACCEPTED as a registered limitation (D-148 ruling 6). Never executed end-to-end by a human. |
| **F2** dwell | READY-evidence-attached | `MIN_CLEAN_DWELL_S=600` + `clean_since` reset semantics (`prewindow_check.sh:37,172-199`) implement the ruled remedy exactly; author threshold untouched. No live 600-s dwell recorded. |
| **F3** clock privilege | READY-evidence-attached | Route re-shaped to the granted write vector + interactive read; sudoers installed and ground-truth verified in custody. The seat decides whether a re-shaped contract satisfies a row that asked to prove a read path. |
| **F4** stale freeze | **STRUCK-AT-2026-08-15** | Nothing to adjudicate on the finding. The seat may wish to note that its M-2 clause was routed to a cold gate that has since ruled (D-140) and that the pack family has moved twice (`_v2`→`_v3`, branch-only). |
| **F5** stale packet | **STILL-OPEN** | No successor/recut packet exists anywhere. Its nearest substitute (the rehearsal card) is itself stale (`_v2`/freeze-0002/`…-20260818`), and the D-149 run-card+GO-receipt pair that may replace it is branch-only and ungauntleted. |
| **F6** templates | READY-evidence-attached **with a named residual** | All four contract violations cured in the runbook (literal values, three keys, pack `calibration_plan.json`, bare `REPO=`) + strict R2 resolver; residual = the example binds `_v2`/`…-20260813` against a live `_v3` family, and the "generate mechanically" alternative was not taken. |
| **F7** launch license | **STILL-OPEN** | Contract ruled and a real admission boundary shipped to main (#156/#157, `launch_window.py`, FD-198 handoff, four downstream refusal reasons). But **A1 is READY [AGENT]**, stage 4 remains, calibration-slot writer enforcement is unimplemented, and the runbook itself says E-10 is "not current authority to launch". |
| **F8** arm-context inline | **STILL-OPEN** | CLI unchanged and still refuses a path; the `$(cat …)` literal is frozen only in a rehearsal card, not in an operator packet (there is none). |
| **F9** 5-min fuse | **STILL-OPEN / NO-REPAIR-FOUND** | Constant unchanged (`arm_readiness.py:6101`); zero operator-visible documentation of the fuse or of the licensed re-arm recovery. |
| **F10** raw `rm -r` | **STILL-OPEN / NO-REPAIR-FOUND** | No `reauthor-clean` exists; the runbook command now deletes **three** namespaces guarded by prose only; the rehearsal card reproduces it. |
| **F11** restore ordering | **STILL-OPEN (partial)** | Runbook now orders and requires recording the restore; still no machine catch. D-149 re-scopes who performs it. |
| **F12** in-horizon TOCTOU | **STILL-OPEN (partial)** | Prohibition is now prominent and bolded; no re-probe at arm/verify/consume; no ABORT row (no packet). D-149 may have removed the human who enforced it. |
| **F13** prewindow patterns | **STILL-OPEN (partial)** | Check 4 restructured under D-127; the agent pattern still omits `claude`/`t3` (`prewindow_check.sh:148-150`). |
| **F14** E-14 arithmetic | **STILL-OPEN / NO-REPAIR-FOUND** | No `date(1)` literal anywhere; E-14 exists only in the un-recut packet. Possibly mooted for no-hands windows — not formally retired. |
| **F15** substring census | **STILL-OPEN (fails closed)** | Scripts unchanged; over-match now confirmed ground truth by the 2026-08-17 census; the repair WO (A4) is still marked BLOCKED on a precondition that appears satisfied. |
| **ED-Q-L8-1** | **ED-ROW closed-with-evidence** (with the read-path caveat) | Five custody files + ground-truth flips; the seat rules whether the re-shaped route satisfies the row as written. |
| **ED-Q-L8-2** | **ED-ROW OPEN** | Builder + card exist and are on main; **no execution, no custody, no receipt**; the card is stale against `_v3`; and E-9a→E-10 is structurally unreachable without a lead-approved committed scratch-ledger route that does not exist. |
| **ED-Q-L8-3** | **ED-ROW closed-with-evidence** (caveats: concurrent-load rail probe; one custody file lead-restored; teardown-census clause thin) | Live sudo demonstrably ran (264 KB plist, ABBA dir, cadence + zero-orphan result). |
| **ED-Q-L8-4** | **ED-ROW OPEN** | No live `quiet_mac_prep.sh` run located, before or after the council; now a sub-step (E-7a) of the un-executed ED-Q-L8-2. |
| **OVERALL (candidate line for the seat)** | **Seat-level candidate: NOT-READY-EVIDENCE-INSUFFICIENT for a READY-CANDIDATE sitting — assembled, not ruled.** | Under charter amendments 11–12 a READY-CANDIDATE sitting binds charter:77-78 (only T0 rows may remain open) and D-149 C1 requires "**ED-QUALIFICATION rows closed**". Two of this seat's four ED rows are open, one blocker (F7) sits behind an open queue row whose own note says "Launch stays NO-GO", one blocker (F5) has no repair at all, and four should-fix/nit rows have no located repair. Against that, four of seven blockers have substantive attached evidence on main. The seat weighs whether the open set is T0-only. |

---

## 5. WHAT A SKEPTICAL SEAT SHOULD PROBE

Each probe names its **falsifier** — the observation that would defeat the attached evidence.

**(a) Staged/scripted vs actually-executed — mandatory, every operator row**

1. **Prove the rehearsal never ran.** `ls -la ~/JouleWise-window-custody/ | grep -i rehearsal` and
   `ls ~/JouleWise-window-custody/ed-qual-20260817/rehearsal`.
   *Falsifier:* a rehearsal custody root containing `arm_readiness.t0.inputs/` with nine files, an
   `arm-0001.json`, and a consumption receipt would close ED-Q-L8-2 and refute this row.
2. **Prove the sudo rows are live, not staged.** `plutil -p
   ~/JouleWise-window-custody/ed-qual-20260817/ed-session-evidence/sampler-checklist-20260818T011840Z.plist
   | head -40` and diff `vector-off-confirmed.txt` against `vector-on-confirmed.txt`.
   *Falsifier:* a plist with zero samples, or identical on/off confirmations, would mean the "live
   sudo" claim rests on scripting rather than execution.
3. **Test whether the card's own commands even parse at this head.** The card binds
   `d117_floor_qwen25_1p5b_v2` and `/Users/edr/JouleWise-measurement-20260818`; the live family is
   `_v3`. `ls /Users/edr/JouleWise-measurement-20260818/configs/campaigns/` and
   `git -C /Users/edr/JouleWise-measurement-20260818 log -1`.
   *Falsifier:* if that checkout already carries `_v3` and freeze-0003, the staleness claim weakens
   to a documentation lag rather than an operator hazard.
4. **Demand the ledger ruling.** `grep -rn "scratch-ledger" docs/` and ask for the lead approval the
   card §8 requires.
   *Falsifier:* a custodied ruling approving a committed scratch-ledger route would make ED-Q-L8-2
   executable-in-principle; its absence means the row's second half is not merely undone but blocked.
5. **Check whether the closed ED rows were ever entered anywhere durable.**
   `grep -rn "ED-Q-L8" --include=* .` in the repo.
   *Falsifier:* any tracked ledger row would refute the "no ID-level tracking" observation; its
   absence means closure is asserted in prose reports, not in the state kernel that D-149 C1 reads.

**(b) Was the error-injection matrix re-run against the CHANGED runbook and the new capture-era / claim-barrier code? — mandatory**

6. **Ask for the delta matrix.** The seat's §3 matrix has 22 cells (A–V) scored against the 2026-08-15
   runbook. Since then: §5C was rewritten (E-4…E-9a wrapper), E-9b/E-9c/E-10 were introduced, the FD-198
   handoff and four `launch_*` refusal reasons landed, the capture-era system and the D-146 claim
   barrier landed, and the pack family moved to `_v3`. Searched for a re-run:
   `grep -rln "error-injection\|error injection" docs/run_reports/2026-08-1[6-9]*.md
   docs/process_traces/2026-08-1[6-9]*/` → **no matches**.
   *Falsifier:* production of any post-2026-08-15 artifact re-scoring cells A–V. Absent that, **the
   matrix that produced this seat's verdict has not been re-derived against the code it now audits**,
   and cells D, E, F, G, L, M, P, Q, S in particular are scored against superseded procedure text.
7. **Re-score the four N cells specifically.** E (launch license — now `launch_window.py`, but A1
   open and calibration-writer enforcement absent), S (`rm -r` — unchanged, now three namespaces),
   T (restore order — doc-only change), R (TOCTOU — prohibition text only).
   *Falsifier:* an executed probe showing direct `window-chain.zsh` invocation now refuses before
   settle would convert cell E from N to C on primary evidence rather than on code reading.
8. **Probe the new surface the old matrix never covered.** The claim barrier (`CLAIM_BEARING_ANCHOR_METHODS`,
   D-146) and capture eras introduce refusal paths an operator can trip. No L8-scoped cell exists for
   `capture_pipeline_superseded` / `capture_pipeline_absent`.
   *Falsifier:* an existing seat report covering operator-visible behaviour of those refusals.

**(c) Did D-149's automation remove a human check that was itself the mitigation for an L8 finding? — mandatory**

9. **F12's mitigation.** The only enforcement of "do not start any new … process" inside the
   20-minute horizon was a human reading the runbook. D-149 C3 checks quietness **once at T-0**
   (`d149-go-receipt-template.md:25-30`). Ask: what prevents the issuing loop from starting a
   polling process at T-0+8 minutes?
   *Falsifier:* a located re-probe at arm/verify/consume, or a documented single-writer lock that
   spans the horizon.
10. **F7's boundary.** Reconcile three texts that currently disagree: runbook `:1051-1056`
    ("Stop at this boundary so Ed can personally inspect… No verdict, author, verifier, or other
    automated command may cross this boundary"), TASK_QUEUE `:536` ("**Ed still launches**"), and
    D-149 (auto-GO, no-hands windows, "REMAINS ED'S: anything needing hands").
    *Falsifier:* a located ruling that names who invokes `launch_window.py` in a no-hands window.
    I found none.
11. **F3/F1's irreducible human inputs.** `capture_t0_step.py:8,43` requires an operator-typed
    trusted-clock UTC literal and a pasted prior-state line; E-4's prior-state read is interactive
    with a password prompt.
    *Falsifier:* a documented unattended route for those two observations. If none exists, a
    "no-hands" window either cannot author T-0 evidence or must synthesize the very inputs the
    TRUSTED-OPERATOR limitation says are the operator's.
12. **The GO receipt's own status.** `d149-go-receipt-template.md:63-66` defers the evaluator "to
    the gauntlet"; `0e96dbb`, `79a4cd0`, `b92b43d` are all branch-only.
    *Falsifier:* a gauntlet record for any D-149 artifact, or their presence on main. `git merge-base
    --is-ancestor <sha> main` returned NO for all three.

**(d) What can a fatigued operator still do wrong at this head that no receipt catches?**

13. **Delete a sibling pack's custody** — runbook `:1016-1021`, unchanged, no shape check, now three
    paths. *Falsifier:* a `reauthor-clean` implementation (none found).
14. **Pause past the undocumented 5-minute arm fuse and read the resulting refusal as a dead night**
    — `arm_readiness.py:6101`, undocumented; the licensed recovery is written nowhere.
    *Falsifier:* any operator-facing sentence naming the 300-s validity or the re-arm recovery.
15. **Arm against the wrong pack family** by following the rehearsal card (`_v2`/freeze-0002) at a
    `_v3` head. *Falsifier:* a refusal that names the family mismatch in a way a 2am operator reads
    as "wrong pack" rather than as a generic identity error — worth an executed probe.
16. **Mistype the ~700-character ARM_CONTEXT inline** inside the 20-minute horizon
    (`generate_arm_readiness.py:61-65` still refuses a path). Exact-key validation catches key
    typos; a **value** typo that is still well-formed (e.g. a wrong `bracket_session_id`) is caught
    only by cross-binding. *Falsifier:* an executed probe showing a plausible value-level typo
    refusing with an operator-legible reason.
17. **Trip the substring census spuriously** (`sampler-checklist.sh:43`) beside any dev activity, and
    "fix" it by killing the wrong process. Fails closed, but it is a fatigue-shaped detour.
18. **Restore network time before close-out completes** — still procedural only (runbook `:627-637`).
19. **Rely on `prewindow_check.sh` to see a forgotten `claude`/`t3` session** — `:148-150` still
    cannot (`codex exec|codex-run|run_campaign|window-chain`). Caught later by the T-0 census, but
    only after the operator has invested the 10-minute dwell.

---

## 6. OPEN ITEMS FROM THIS ROW

- **F5 (blocker) — no successor/recut arm packet exists anywhere.** The FINAL packet at
  `~/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md` is unmodified;
  no repair artifact of that class was located (`grep -rln "arm-packet" docs/`). Everything WO-L8-5
  bundled into the packet — the paste-ready E-9a/b/c literals, the horizon, the fuse, the re-author
  rule, the E-14 `date(1)` literal, the F12 ABORT row — has no home.
- **F7 (blocker) — WO-LAUNCH-BINDING is still queue row A1, READY [AGENT]**, stage 4 outstanding,
  calibration-slot writer enforcement unimplemented; the runbook itself declares E-10 "not current
  authority to launch" and the queue note says "Launch stays NO-GO."
- **F8 — `--arm-context` still refuses a custody path**; the `$(cat …)` literal exists only in the
  rehearsal card.
- **F9 — NO-REPAIR-FOUND.** The 5-minute arm-receipt fuse (`arm_readiness.py:6101`) is still
  documented nowhere operator-visible, and the licensed re-arm recovery is undocumented.
- **F10 — NO-REPAIR-FOUND.** No governed `reauthor-clean`; the raw `rm -r` now spans three namespaces.
- **F11 — no machine catch** for restore-before-close-out; documentation-only improvement.
- **F12 — no re-probe** of process state at arm/verify/consume; the prohibition is prose only, and
  D-149 may have removed the human who honoured it.
- **F13 — `prewindow_check.sh` agent pattern still omits `claude`/`t3`** (`:148-150`).
- **F14 — NO-REPAIR-FOUND.** No `date(1)` literal for the do-not-return-before time.
- **F15 — ED-session census still substring-based**, and its repair WO (A4 `WO-CENSUS-SEMANTICS`)
  remains marked **BLOCKED — ED-Q-L9-3** (TASK_QUEUE `:538`, `:632`) even though that fixture was
  captured 2026-08-17 — a stale kernel row, or an unstated stricter precondition.
- **ED-Q-L8-2 — OPEN, and the verdict's "most valuable Ed hour" is unspent.** Builder and card
  exist on main (`ad14ac4`); **no execution**, no scratch custody root, no receipts. The card is
  stale (`_v2`/freeze-0002/`…-20260818` vs live `_v3`/freeze-0003), and E-9a→E-10 is structurally
  unreachable without a lead-approved committed scratch-ledger route that does not exist.
- **ED-Q-L8-4 — OPEN.** No live `quiet_mac_prep.sh` run located at any date after 2026-07-17
  (`bash -n` only). It is now E-7a inside the un-executed rehearsal, so it inherits ED-Q-L8-2's blockage.
- **ED-Q-L8-1 read-path caveat.** The row asked for a proven read path or a ratified `sudo -v`
  warm-up; neither was delivered. The defect was dissolved by re-shaping the contract (write-vector
  probe + interactive prior-state read). Adjudicable, not automatic.
- **The L8 error-injection matrix has NOT been re-run** against the rewritten §5C, the E-9b/E-9c/E-10
  sequence, the FD-198 handoff, the capture-era system, or the D-146 claim barrier. Searched
  `docs/run_reports/2026-08-1[6-9]*.md` and `docs/process_traces/2026-08-1[6-9]*/` for
  "error-injection" — no matches. This is the seat's own instrument, and it is stale.
- **D-149's automation has been audited by nobody.** The GO-receipt evaluator is explicitly deferred
  to a future gauntlet (`d149-go-receipt-template.md:63-66`); until then "mechanical evaluation" is a
  markdown checklist filled by the issuing agent. D-149 (`0e96dbb`), the template (`79a4cd0`) and the
  shakedown run card (`b92b43d`) are **all branch-only** (`git merge-base --is-ancestor … main` = NO).
- **Unresolved authority conflict:** runbook `:1051-1056` and TASK_QUEUE `:536` both reserve the
  physical launch to Ed; D-149 authorises no-hands windows. No ruling naming the invoker of
  `launch_window.py` in a no-hands window was located.
- **F1's residual is an ACCEPTED LIMITATION, not a closed defect** (D-148 ruling 6 + the
  TRUSTED-OPERATOR registration). Whether an accepted limitation satisfies a READY-CANDIDATE seat is
  the seat's call, not the assembler's.
- **Family staleness runs through the operator surface**: runbook `window.env` example binds `_v2` /
  `…-20260813`; rehearsal card binds `_v2` / freeze-0002 / `…-20260818`; the live family is `_v3` /
  freeze-0003 and lives **only on the branch**.
- **ED-QUALIFICATION rows are not tracked by ID** anywhere in the repo (`grep -rn "ED-Q-L8"` outside
  the council directory → zero hits), while D-149 C1 conditions auto-GO on "ED-QUAL rows closed".
  There is no mechanical list for that condition to read.
- **Three of the seat's six unexecuted obligations remain unexecuted** (`quiet_mac_prep.sh` live;
  E-9 reservation double-reserve/live-writer against a ledger copy; runbook §10 refusal-row
  completeness for the 2am operator — and §10 has since grown four new `launch_*` rows).
