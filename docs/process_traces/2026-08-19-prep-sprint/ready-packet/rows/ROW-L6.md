# ROW L6 — SEAM READER A (producer→consumer obligation graph, CONTRACT lens) — GATING seat, charter v2 full-tier

> **Assembler note (mechanical, not adjudicated).** This row attaches evidence and names
> candidate dispositions. It does **not** grade the seat READY. The verdict's standing caution
> applies verbatim: "**The work-order program is NOT CERTIFIED COMPLETE** … Closing all listed
> work orders does not entitle READY" (`docs/process_traces/2026-08-15-readiness-council/council-verdict.md:18-22`).

**Tree state at assembly.** Read-only worktree `…/scratchpad/wtS0`, branch
`impl/r2-s0-mint-resolver`, **HEAD `b92b43d`** ("Shakedown-v3 first-light run card (prep item 6b)").
The task brief named `4597ad4` and `raw/CHANGE-UNIVERSE-BRIEF.md:4` names `4597ad4`; the
`_ASSEMBLER-BRIEF.md:12` names `d10881b`. Both are ancestors of the actual HEAD — the tree advanced
one commit past `4597ad4` during assembly. **Commit count from the audit baseline `8937dec` to HEAD
is 215, not the 214 the brief states.**

**AMENDMENT (post-assembly).** The worktree HEAD moved again while this row was being written —
`b92b43d` → `7305e0d` → `45e0229` → `48f337b` → **`2243137`** (now 219 commits from `8937dec`).
Verified: `git diff --name-only b92b43d..2243137 | grep -E '^(joulewise|scripts|configs)/'` returns
**NOTHING** — no code, script, pack, registry or config bytes changed, so every code and config
citation in this row holds at `2243137`. The four new commits touch `README.md`, `RUN_STATE.md`,
`TASK_QUEUE.md`, `WINDOW_STATUS.md`, `docs/decision_log.md`, `docs/process/state_kernel.json`, and
`docs/process_traces/2026-08-19-prep-sprint/**` (paper-staging skeletons, a fresh-pass gate report,
and an earlier generation of the READY-packet row files landed into custody). **A seat should
re-verify the doc line numbers cited from `RUN_STATE.md`, `TASK_QUEUE.md` and `docs/decision_log.md`,
which those commits edited.** That the audited tree advanced four times during a single assembly
pass is itself material to the Phase-3 "audit at a pinned head" discipline.

`origin/main == main == 0099382`; `1d3873b`, `5e38f1e`,
`eb7f6c6`, `94dc3b3`, `8b2b021`, `0e96dbb` and the whole Phase-2 transaction are **BRANCH-ONLY**
(not on `origin/main`). Where evidence lives is stated per item below.

---

## 0. Seat identity and 2026-08-15 result

| Field | Value | Citation |
|---|---|---|
| Seat ID | `L6-SEAM-READER-A` | `sitting-packet-FINAL.md:16` (packet hash `054da78691dc175b`) |
| Tier | GATING | `sitting-packet-FINAL.md:24` |
| Recorded verdict | **NOT_READY** | `sitting-packet-FINAL.md:24`; `raw/L6-triage.md:7`; seat report §6 `seat-reports/L6-SEAM-READER-A-report.md:84-86` |
| Coverage | **34 / 40** (evidence_universe_count = 40) | `sitting-packet-FINAL.md:24`; `raw/L6-triage.md:8`; seat report §2 `:12-14` |
| Findings | 8 = 2 blockers / 3 should-fix / 3 nits | `sitting-packet-FINAL.md:24`; `raw/L6-triage.md:9` |
| Falsifiers | 5 (all refused) | `sitting-packet-FINAL.md:24`; seat report §4 `:69` |
| Unexecuted obligations | 6 | `sitting-packet-FINAL.md:24,201-206` |
| ED-QUALIFICATION rows | 2 | `sitting-packet-FINAL.md:24,176-177` |
| Effective audit baseline | `8937dec` (= manifest head `ac3fe1d` + 3 files) | `council-verdict.md:7-8` |
| Coverage adversarially tested? | **NO** — only L2's denominator was attacked, and it FELL | `council-verdict.md:18-22` |

Seat's own consumption-soundness statement (relevant to how a seat weighs everything below):
"across everything probed, **no missing, stale, tampered, or foreign artifact was silently
consumed — every seam refused**. … The chain fails closed; it currently cannot ARM."
(`seat-reports/L6-SEAM-READER-A-report.md:82`).

Charter significance: L6 is one of the two paired independent seam readers, and its B1 is the
**layer-6 instance of the T6 five-layer producer-gap specimen** — "the producer-gap moved one seam
upstream, into the inputs of the producer that closed §0.6" (`seat-reports/L6-SEAM-READER-A-report.md:73`).

---

## 1. FINDINGS — original text verbatim, with citation

### F1 — [blocker] B1 — The T-0 evidence author's own inputs have no producer: no tool, no runbook step, no packet step

- **severity:** `blocker`
- **title (verbatim):** `B1 — The T-0 evidence author's own inputs have no producer: no tool, no runbook step, no packet step`
- **file_line (verbatim):** `joulewise/arm_readiness_evidence_t0.py:42,132-139,506,556,601; docs/phase_2/window_runbook.md:812-827`
- **failure_scenario (verbatim):**

> The funded night reaches §5C's post-E-9 authoring step; author_arm_evidence_t0.py refuses evidence_author_t0_clock_attestation_missing (demonstrated live in probe P3) because nothing has created CUSTODY/PACK_ID/arm_readiness.t0.inputs/ — the author requires clock-attestation.json, arm-context.json, launch-manifest.json and six command captures (clock-prior-state, clock-disable, quiet-mac-prep, prewindow-check, ledger-readiness, ledger-reservation) as canonical JSON with boot-bound monotonic-ns fields no human can hand-produce; no repo tool writes joulewise.arm_readiness_t0_command_capture.v1 (grep: only the author itself references the schema), the runbook never names arm_readiness.t0.inputs, and the FINAL arm packet predates the author entirely. Night ends NO-GO — or worse, the operator hand-crafts nine JSON files at 2 a.m., the exact anti-pattern the readiness machinery exists to prevent.

- **Citation:** `raw/L6-triage.md:12-14`; sitting packet §3 `sitting-packet-FINAL.md:39-41`; seat report §5 `:73` and graph node 12 `:33`.
- **Post-verdict adjudication:** NOT struck. Cross-confirmed by L8-B1 (`sitting-packet-FINAL.md:84-86`) and by **both** cluster-B refuter lenses: `refuter-outputs/sol-refuter-B-contract.md` F1/F2 CONFIRMED, `sol-refuter-B-execution.md` F1/F2 CONFIRMED ("F1 and F2 should produce one work order, not two"). Refuter-verdicts fold: `refuter-outputs/refuter-verdicts.md:62-79`. Work-order form: **integrated WO-T0-PRODUCER** (`council-verdict.md:82-83`).
- **Refuter correction on record (contract lens):** "Nine filenames are implementation preconditions, not D-134 names" (`refuter-verdicts.md:65-66`).
- **Refuter correction on record (execution lens):** the phrase "no human can hand-produce" is "literally overstated: a human can fabricate these plain JSON objects. That worsens, rather than refutes, the authenticity defect" (`sol-refuter-B-execution.md`, F1 prose).

### F2 — [blocker] B2 — Committed freeze evidence is already past its 24 h monotonic horizon; every future window requires an undocumented full freeze-refresh lane

- **severity:** `blocker`
- **title (verbatim):** `B2 — Committed freeze evidence is already past its 24 h monotonic horizon; every future window requires an undocumented full freeze-refresh lane`
- **file_line (verbatim):** `joulewise/arm_readiness.py:2943-2975,3712-3719; docs/phase_2/window_runbook.md:726-742,812-830`
- **failure_scenario (verbatim):**

> Live reading on the freeze boot session: now-monotonic 1,996,764 s > valid_until 1,986,799 s — all 11 generic PACK evidence receipts frozen 2026-08-13 are expired. generate_arm_receipt folds evidence expirations into the arm receipt's valid_until (min(...)), so any arm receipt issued now is expired at birth; verify/consume then refuse readiness_record_expired (arm_readiness.py:3952-3955). Cure = re-author 11 receipts + new freeze receipt + plan-tree re-pin + commit + review + fresh dry-run, same boot session as ARM and ≤24 h before it — a cycle no operative document names: §4 presents freeze as 'before quiet time' desk work, §5C's re-author rm covers only the two T-0 namespaces, and the reboot-fence paragraph says only 'generate new receipts'. Fails closed at every probe point, so no consumption unsoundness — but a required output (a valid GO arm receipt) currently has no producible path under the frozen packs + current runbook alone, and the refresh commits void the audit baseline per charter amendment 12.

- **Citation:** `raw/L6-triage.md:16-18`; sitting packet §3 `sitting-packet-FINAL.md:44-46`; seat report §5 `:74`, probe F2d `:69`.
- **Post-verdict adjudication:** NOT struck. Confirmed by **both** cluster-A lenses. Contract: "L6-B2 refresh lane: CONFIRMED w/ qualification (partial prose exists; freeze CLI cannot reissue — freeze-0001 hardcoded, mutated:false short-circuit; no successor-pack command anywhere)" (`refuter-verdicts.md:7-8`). Execution: "F2 (no refresh lane) CONFIRMED: producer exists, operative refresh lifecycle for a frozen pack does not" (`refuter-verdicts.md:85-86`; `sol-refuter-A-execution.md` F2 prose). **Remedy corrected by the contract lens:** "in-place re-author NOT contract-valid (D-131 requires successor pack+custody root)" (`refuter-verdicts.md:5-6`), and the remedy "must include a successor pack identity/root, regenerated U11 binding as applicable, 11 new generic receipts, new freeze receipt and plan pin, commit/review/dry-run, canonical-checkout synchronization, and audit-baseline re-pin" (`sol-refuter-A-execution.md`, F2 prose). Routed to **Phase 0 R1 ruling** + **Phase 2 atomic re-freeze** (`council-verdict.md:74-75,97-100`).

### F3 — [should_fix] S2 — D-117 two-stage mint freeze: the stage-1 desk pin artifact (floor_mint_pin_requirements.v2) has no committed instance and nothing fails closed on its absence

- **severity:** `should_fix`
- **file_line (verbatim):** `scripts/mint_floor_artifact_generalized.py:1391-1392; docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:368-403`
- **failure_scenario (verbatim):**

> DESIGN-MEMO §Two-stage mint freeze requires desk-time pins in a non-mintable pin_requirements.v2 artifact before collection; `git ls-files | grep pin_requirements` returns nothing, and the mint's only reference is a guard refusing it AS a pinset (mint_floor_artifact_generalized.py:1391-1392). A final pinset constructed entirely post hoc after the window would be mechanically indistinguishable from one honoring the two-stage freeze — the pre-registration value the ruling ordered is silently absent.

- **Citation:** `raw/L6-triage.md:20-22`; sitting packet §4 `:120`; seat report §5 `:75` and graph node 31 `:52`.
- **Post-verdict adjudication:** no separate refuter (should-fix tier under C-028 gets ≤1; none in the harvested set addresses S2). Work order **WO-L6-4** (`raw/L6-triage.md:52`), which the verdict folds into "should-fix batch" (`council-verdict.md:85-87`).

### F4 — [should_fix] S3 — §12's postcollection backup receipts have no producer: backup_runs.sh emits no receipt and no hash

- **severity:** `should_fix`
- **file_line (verbatim):** `scripts/backup_runs.sh:38-42,58-67; docs/phase_2/window_runbook.md:1475-1481,1518-1526`
- **failure_scenario (verbatim):**

> Close-out requires 'each successful postcollection backup receipt path and SHA-256 … separately for the claim and bound roots'; backup_runs.sh writes only an unhashed one-line backup.log entry and §11 shows a single claim-root invocation. On the night the operator either cannot complete §12 as written or improvises an unhashed record; nothing downstream gates on backup, so a failed backup surfaces only in the human record.

- **Citation:** `raw/L6-triage.md:24-26`; sitting packet §4 `:121`; seat report §5 `:76`, graph node 28 `:49`.
- **⚠ ID-COLLISION WARNING FOR THE SEAT.** This L6 finding is labelled **S3** in the seat's own text but is carried as **triage F4**. `council-verdict.md:44-45` Disposition 4 strikes "**F4's timing premise**" — that is **cluster-B refuter F4 = L8-B3 (the `sudo -n systemsetup` / D-004 privilege finding)**, *not* this L6 backup-receipt item. Cross-check: `refuter-verdicts.md:69-70,112-114` and `sol-refuter-B-execution.md` F4 prose ("the claim that the current E-7b necessarily cools the timestamp is false"). **Nothing in L6's row was struck.** The seat should not read Disposition 4 as touching this finding.

### F5 — [should_fix] S4 — The FINAL arm packet (the operator's night document, cited by the audit-baseline manifest) is stale against the baseline runbook

- **severity:** `should_fix`
- **file_line (verbatim):** `~/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md:480 (off-repo custody)`
- **failure_scenario (verbatim):**

> The packet's E-9a jumps from E-9 straight to `generate_arm_readiness.py arm` with no T-0 authoring step, never mentions arm_readiness.t0.inputs, and still says 'Expect a refusal tonight unless §0.6 has been resolved' — §0.6 is resolved by the T-0 author at this baseline. An operator following the packet verbatim arms without authored T-0 evidence and gets a wall of readiness refusals with no packet row explaining them.

- **Citation:** `raw/L6-triage.md:28-30`; sitting packet §4 `:122`; seat report §5 `:77`, graph node 38 `:59`.
- **Post-verdict adjudication:** cross-confirmed as L8-B5 (blocker at that seat, `sitting-packet-FINAL.md:104-107`) and CONFIRMED by the execution lens with the packet SHA-256 `5c05f6fe99b547467372b90a61957163c47c891f6ff0c6414a4d3a7c40e47a96` recorded (`sol-refuter-B-execution.md` F5 prose; `refuter-verdicts.md:71-72`). Remedy ruled: "**issue reviewed SUCCESSOR packet; preserve old as custody**"; "Merely editing the old packet would leave its frozen-head claims false." Sequenced to **Phase 2, after the T-0 repair passes end-to-end at the exact reviewed head** (`council-verdict.md:97-100`, Opus W8).

### F6 — [nit] N1 — window_duration_margins_receipt.v1 has no machine consumer; §11 ordering is unenforced

- **severity:** `nit`
- **file_line (verbatim):** `joulewise/window_duration_margins.py; scripts/record_window_duration_margins.py:19`
- **failure_scenario (verbatim):**

> Only scripts/record_window_duration_margins.py (writer) and tests reference the schema; extraction and mint proceed regardless. A tired operator who skips §11 loses the comparative-cell margin record with no mechanical signal — discovered only if a human audits the close-out record.

- **Citation:** `raw/L6-triage.md:32-34`; sitting packet §4 `:123`; seat report `:78`, graph node 27 `:48`. Nits receive no refuter under C-028.

### F7 — [nit] N2 — PRIVILEGE_INSTALLATION evidence kind has no producer anywhere in the repo

- **severity:** `nit`
- **file_line (verbatim):** `configs/arm_readiness/d117_row_registry_v1.json (privilege.* rows); joulewise/arm_readiness.py:2289-2303`
- **failure_scenario (verbatim):**

> Harmless while clock_route stays frozen at MANUAL (the four privilege.* rows evaluate NOT_APPLICABLE — confirmed in the P1 census); any future arm context using the clock-helper route makes four rows applicable with no production path, guaranteeing NO-GO with no tooling recourse. Record so the gap is chosen, not discovered.

- **Citation:** `raw/L6-triage.md:36-38`; sitting packet §4 `:124`; seat report `:79`, census statement `:63`.

### F8 — [nit] N3 — The arm-time freeze-evidence replay skips the monotonic-horizon check; defense is one hop downstream

- **severity:** `nit`
- **file_line (verbatim):** `joulewise/arm_readiness.py:2955-2960 vs 3712-3719,3952-3955`
- **failure_scenario (verbatim):**

> _freeze_evidence_for_arm authenticates freeze evidence with expected_boot_session_id but no now_monotonic_ns, so FREEZE_AND_ARM rows can show PASS from horizon-expired evidence inside the arm receipt; the expiry is enforced only via the valid_until min-fold plus verify/consume. Any future direct consumer of row verdicts (none today) would read PASS rows from expired evidence.

- **Citation:** `raw/L6-triage.md:40-42`; sitting packet §4 `:125`; seat report `:80`.
- **Note:** this is the same code seam as L7 FINDING 1 (should_fix at that seat). The two seam readers **assigned different severities to the same mechanism** — L6 nit, L7 should_fix. See ROW-L7 §1 F1 and probe 6 below.

### Unexecuted obligations carried by this seat (verbatim, all six)

> - Did not execute generate_arm_readiness.py freeze/dry-run/arm/consume as CLIs end-to-end (freeze mutates pack bytes; arm requires the B1 inputs that do not exist; tree had to stay byte-identical) — authentication internals were exercised by direct calls instead
> - Did not run the collection-plane producers live (run_campaign, validate_powermetrics_fiducial, reserve_calibration_window_bracket) — no live measurement permitted; their seams verified by contract+code reading only, deep audit owned by seats L2/L3/L4
> - Did not execute extraction→mint on a synthetic window (seat L10's sacrificial lifecycle owns this); mint consumption verified by import/code reading only
> - Did not deep-trace the claims-index/claims-lint consumption seam beyond identifying producer and consumer files (post-paper plane, thinner risk)
> - Did not resolve whether the t0.ledger_reservation predicate's expected_plan_sha256 (pack plan_tree sha) and the reservation's FROZEN_PLAN sha are the same identity — flagged to seat L2 (calibration acquisition) rather than guessed
> - Could not read the FROZEN_PLAN/window.env instance (off-repo by design; none exists yet for the next window)

Citation: `raw/L6-triage.md:62-75`; `sitting-packet-FINAL.md:201-206`.

---

## 2. WHAT CHANGED SINCE 2026-08-15

### F1 / B1 — T-0 input producer — **SUBSTANTIALLY REPAIRED; the follow-up lane DID land; the contract was HONESTLY WEAKENED**

| Item | Value |
|---|---|
| Work order | **WO-T0-PRODUCER**, `TASK_QUEUE.md:106` (Completed Queue Items) |
| Merge | **PR #152**, merge commit `a61ac92` — "WO-T0-PRODUCER: T-0 acquisition capture tool + R2 resolver + D-127 clock route + dwell/env hardening (#152)", 2026-08-15 |
| Reviewed head cited by the queue row | `9e8936a` ("Merge main into wo-t0-producer (decision-log union)") — **`9e8936a` is BRANCH-ONLY, not on `origin/main`**; `a61ac92` itself **is** on `origin/main` |
| Code landed | `scripts/capture_t0_step.py` (38,135 bytes, executable), `tests/test_capture_t0_step.py` |
| Decision IDs | D-134 cl.6 (superseded by 65cc0f3), D-127, D-148 cl.6 |

**Coverage check performed by this assembler.** `scripts/capture_t0_step.py:59-66` defines
`STEP_FILENAMES` for exactly the six captures L6 enumerated —
`clock-prior-state`, `clock-disable`, `quiet-mac-prep`, `prewindow-check`, `ledger-readiness`,
`ledger-reservation` — writing into `INPUT_DIRECTORY = "arm_readiness.t0.inputs"` (`:41`). The three
remaining inputs are derived, not hand-authored: `arm-context.json` at `:518-528`
(validated through `readiness.validate_arm_context`, `:448`), the launch manifest under
`LAUNCH_MANIFEST_SCHEMA` at `:521`, the clock attestation under `CLOCK_ATTESTATION_SCHEMA` at `:588`.
Ordering and no-clobber are enforced (`:681-733`, `:951-962`). **All nine of L6's named inputs now
have a shipped producer.**

**Runbook step now exists.** `docs/phase_2/window_runbook.md:913,922,931,942,952,963` name the six
`capture_t0_step.py` invocations as E-4…E-9a; `:970` and `:1020` name
`arm_readiness.t0.inputs` explicitly; `:994` names E-9b as the author step. L6's "the runbook never
names arm_readiness.t0.inputs" is **no longer true at this head**.

**The F4 honest-contract follow-up lane the TASK_QUEUE row defers to — IT LANDED.**
`TASK_QUEUE.md:106` says "the F4 honest-contract deltas ride the follow-up t0-producer lane per the
2026-08-15 provenance ruling." Located, all three **on `origin/main`**:

- `65cc0f3` (2026-08-15) — "T-0 F4 honest contract: D-134 cl.6 overclaim superseded (production-interface/ceremony rule, no operator-fabrication-resistance claim), TRUSTED-OPERATOR limitation v1 registered, public execute/monotonic_ns/utc_now injection seam removed from capture_t0_step (module-private test hook), runbook + docstrings corrected" — 6 files, +142/−10.
- `d8d2022` (2026-08-15) — "Lens F1 fix: E-4 prose names both registered irreducible operator observations".
- `32cf987` (2026-08-16) — "Final-head pass cures: D-134 amendment blockquote now names E-4's two registered observations … docstring scoped … (absolute-only overclaim removed)".

Custody of the ruling: `docs/process_traces/2026-08-15-t0-capture-provenance-consult/`
(`consult-prompt.md`, `consult.md`). Registered limitation text:
`docs/decision_log.md:9630` and `:9669` — "**REGISTERED LIMITATION (v1):** T-0 capture provenance is
TRUSTED-OPERATOR"; runbook statement at `docs/phase_2/window_runbook.md:885`; session record at
`docs/run_reports/2026-08-16-t9-session.md:132`.

**What the repair does NOT claim (material to the seat).** `scripts/capture_t0_step.py:1-11`
docstring: "The production CLI is a trusted-operator ceremony interface, **not independent producer
attestation**. … v1 does not defend against deliberate operator fabrication."
`window_runbook.md:880-890`: "Direct JSON authorship, modified library invocation,
clock/execution substitution, or edits to `arm_readiness.t0.inputs` violate procedure **but are not
mechanically detectable in v1**." Ed **accepted** this class as a registered limitation —
D-148 clause 6 (`docs/decision_log.md:171`): "the risk-appetite family (recorder race / **T-0 capture
provenance** / hostile same-UID injection / forged launch-context) is ACCEPTED AS REGISTERED
LIMITATIONS." So the *producer gap* closed; the *authenticity* property the seat's scenario invoked
("no human can hand-produce") was retracted rather than delivered.

**Terminal-review-trailer producer gap (the Addendum's remedy).** `council-verdict.md:121-131` and
`sol-refuter-singlelens.md:239-247` order "a lead-owned terminal-review attestation step whose commit
the superseding manifest pins, with the measurement checkout and T-0 author operating at the attested
commit." At this head the remedy exists in **two halves**:
- **CODE (verifier, fail-closed):** `scripts/capture_t0_step.py:288-317` `_verify_terminal_review()`
  refuses `evidence_author_t0_capture_terminal_review_missing` unless HEAD carries exactly one each of
  `JouleWise-Terminal-Review: PASS`, `-Tree-Oid: <current tree>`, `-Pack-Sha256: <current pack digest>`;
  duplicated independently in `joulewise/arm_readiness_evidence_t0.py:931-937`.
- **DOCUMENTED CEREMONY (no code producer):** `docs/phase_2/window_runbook.md:812-838` gives the literal
  `git commit --allow-empty --cleanup=verbatim … -m 'JouleWise-Terminal-Review: PASS' …` recipe, and
  `docs/process/rehearsal-operator-card.md:30` gives an executable one-liner form.
  **No script creates the attestation commit** — the "producer" is a human/lead git ceremony.
- **PHASE-3 HALF NOT DONE:** the superseding manifest that pins the attested commit does not exist —
  `docs/process/audit-baseline-manifest.json:3` still names the 2026-08-13 packet and the old baseline.
- **STALE PATH IN THE ORDERED STEP:** `window_runbook.md:813` still says
  `cd /Users/edr/JouleWise-measurement-20260813`, while the live measurement checkout is
  `/Users/edr/JouleWise-measurement-20260818` (`RUN_STATE.md:167,241,383`;
  `docs/process/rehearsal-operator-card.md:3`).

**Candidate disposition:** READY-EVIDENCE-ATTACHED, with three named residuals (trusted-operator
contract weakening accepted by D-148 cl.6; terminal-review producer is ceremony + verifier, not a
tool; the Phase-3 pinning manifest absent).

### F2 / B2 — freeze horizon + refresh lane — **THE LANE WAS BUILT AND RUN TWICE, AS SUCCESSOR PACKS; the horizon SEMANTICS were not changed**

The refuter-corrected remedy (successor pack + custody root, not in-place re-author) is what was
actually executed, through the R1/R2 rulings:

| Element | Evidence | Where it lives |
|---|---|---|
| R1 ruling (freeze-evidence lifecycle) | `docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/` (`consult.md`, `coldgate-adjudicator-ruling.md`, `coldgate-opus-refuter-findings.md`) | branch |
| Freeze numbering | `docs/process_traces/2026-08-17-freeze-numbering-consult/`; commit `b6553fd` "WO-FREEZE-NUMBERING delta-8: replay reauthenticates the successor; v2 freeze sequences carry the predecessor" | branch |
| Freeze-status byte semantics | **D-140** (cold gate, 3-seat concurrence) — `docs/decision_log.md:173`; custody `docs/process_traces/2026-08-18-freeze-semantics-coldgate/` (14 files incl. `12-cold-adjudicator-ruling.md`, `13-opus-contract-refuter.md`, `14-composed-verdict.md`) | branch |
| Registered residuals | **D-141** — `docs/decision_log.md:174`; `docs/risk_register.md` R-019, R-020 | branch |
| Horizon policy ruling | **D-139 A3** (Ed, 2026-08-17): "Phase-2 reserved defaults APPROVED (uniform `_v2` successor pack IDs; chain-monotonic `freeze-0002` with explicit predecessor bindings; **existing operational horizons**)" — `docs/decision_log.md:164` | branch |
| Boot-session amendment | **D-137** — `docs/decision_log.md:162` | branch |
| `_v2` family + freeze-0002 | executed 2026-08-18 at `/Users/edr/JouleWise-measurement-20260818`; digests table `docs/process/ed-morning-packet-2026-08-18.md:95-97` | branch |
| **R2 ruling → `_v3` family** | **D-147** — `docs/decision_log.md:170`; ONE home `docs/process_traces/2026-08-19-r1-r2-codesign/14-r2-ruling.md` | branch |
| `_v3` freeze-0003 mints | `5e38f1e` (1p5b_v3), `eb7f6c6` (7b_v3), `94dc3b3` (contrast_v3), `8b2b021` (S5 confirmation table); U11 projections `3d05982`, `6fd8bce`, `74632e3` | **BRANCH-ONLY** |

**Machinery changes verified in code at this head:**
- Freeze receipt schema is now `joulewise.arm_readiness_freeze_receipt.v2` with an explicit
  `predecessor` block naming the prior receipt id/path/sha (verified by reading
  `configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json`;
  predecessor `freeze-0002` sha `1277103b…`). Successor lineage is now a first-class receipt field —
  the "freeze-0001 hardcoded" defect the contract refuter named (`refuter-verdicts.md:7-8`) is gone.
- Evidence receipts now carry `head_commit` in addition to `boot_session_id` and
  `valid_until_monotonic_ns`.
- An R1 lifecycle layer exists in code: `joulewise/arm_readiness.py:45`
  `R1_ROW_REGISTRY_SCHEMA = "joulewise.arm_readiness_row_registry.v2"`,
  `R1_EVIDENCE_FRESHNESS_CLASSES` (`:676`), `_R1_EVIDENCE_POLICY_KEYS` (`:510`), and a
  `V1_GRANDFATHERING` `EvidenceLifecycleError` inside `_authenticate_generic_evidence_item`.

**⚠ THE R1 LIFECYCLE IS PRESENT BUT NOT ACTIVATED.** The only committed registry is
`configs/arm_readiness/d117_row_registry_v1.json`, whose `schema_version` is
`joulewise.arm_readiness_row_registry.v1` and which has **no `freeze_evidence_lifecycle` block**
(verified by parsing the file). `git grep -l "arm_readiness_row_registry.v2" -- configs` returns
nothing. `freeze-0003.json`'s `row_registry` field points at that same v1 file
(sha `d248fdc5…`). In `_freeze_evidence_for_arm` the `lifecycle_registry` (and therefore
`expected_head`) is `None` whenever the registry is v1 — so the new head-binding and the
V1_GRANDFATHERING refusal are **dormant on the production packs**. D-148 clause 5 confirms this is
open work: "R1 row-registry **reserved values → COUNCIL** (Ed defers…)" (`docs/decision_log.md:171`);
RUN_STATE prep item 4 is the registry-values council packet (`RUN_STATE.md:38-42`).

**⚠ LIVE HORIZON PROBE RUN BY THIS ASSEMBLER (read-only, `time.monotonic_ns()` + parsing committed bytes).**

```
now_monotonic_ns 2415145103251500  (= 2,415,145 s)
boot_session_id  DA90818C-9C31-45D0-8813-DEAE65FBA143   (unchanged since the 2026-08-13 freeze)
d117_floor_qwen25_1p5b_v3      n=11  min valid_until 2468742407178458  expired=False
d117_floor_qwen25_7b_v3        n=11  min valid_until 2468774933440083  expired=False
d117_contrast_qwen25_1p5b_vs_7b_v3  n=11  min valid_until 2468792444508708  expired=False
all 33: boot_session_id da90818c-…, head_commit 1d3873bb7a37e9363202429f14587c85a0b4efc0
```

So: **the 33-receipt lapse the finding recorded is CURED for now — with ~53,597 s ≈ 14.9 hours of
headroom remaining at probe time**, on the same boot session, and it will lapse again on the same
24 h clock. Two facts a seat must weigh against that:
1. `head_commit` for all 33 is `1d3873b` ("S3: d117 `_v3` pack family emitted…"), which is **28
   commits behind HEAD `b92b43d`** and **not on `origin/main`**. Under the *activated* R1 lifecycle
   this head drift would refuse; under the dormant v1 registry it does not.
2. Charter amendment 12 exposure is unresolved: the refresh commits that cured the lapse are exactly
   the pack-byte changes that void the audit baseline, and the superseding manifest
   (`council-verdict.md:68-70,102-104`, Phase 3) has **not** been issued —
   `docs/process/audit-baseline-manifest.json` still pins the pre-refresh world.

**Candidate disposition:** STILL-OPEN (mechanism repaired and executed; contract-level closure —
R1 registry activation, Phase-3 supersession, and the standing 24 h re-run obligation — outstanding).

### F3 / S2 — stage-1 `floor_mint_pin_requirements.v2` — **NOTHING CHANGED**

`git ls-files | grep -i pin_requirement` returns **nothing** at HEAD `b92b43d`, exactly as at the
baseline. No committed instance for alpha, beta, or gamma; no ruling located that the packs'
extraction specs + plan trees subsume stage 1 (WO-L6-4's alternative); no mint-side or close-out-side
existence check added. **NO-REPAIR-FOUND.** Searched: `git ls-files | grep -i pin_requirement`;
`git grep -n "pin_requirements"`; TASK_QUEUE completed table (`:98-115`) and current queue; the
should-fix batch commits.

### F4 / S3 — hashed postcollection backup receipts — **NOTHING CHANGED**

`git log --oneline 8937dec..HEAD -- scripts/backup_runs.sh` returns **zero commits** — the file has
not been touched in the entire 215-commit span. `grep -n "sha256\|receipt\|shasum" scripts/backup_runs.sh`
returns **no matches**. §12's two-root hashed-receipt obligation is still unproducible.
**NO-REPAIR-FOUND.**

### F5 / S4 — the FINAL arm packet — **NOT REGENERATED; and the nearest artifact is itself now stale**

- `docs/process/audit-baseline-manifest.json:3` still reads
  `"arm_packet": "~/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md (off-repo custody)"`.
- The verdict sequences the successor packet after the Phase-2 re-freeze and after the T-0 repair
  passes end-to-end at the exact reviewed head (`council-verdict.md:97-100`). The re-freeze ran twice
  (`_v2`, `_v3`), the end-to-end pass has **not** (see §3, dress rehearsal OPEN).
- M-2 obligation still live: "the successor arm packet must cite it until the re-freeze retires it"
  (`council-verdict.md:38-40`; `docs/council_log.md:3614,3746`;
  `docs/process_traces/2026-08-15-m2-coldgate/composed-verdict.md:20`).
- The nearest new operator document is `docs/process/rehearsal-operator-card.md`, which self-declares
  at `:3` "This is **qualification choreography evidence, never claim evidence**", and which targets
  the **`_v2`** alpha pack (`:30,38,50-110`) while the live family is `_v3`. It is not a successor arm
  packet and is already a family behind.

**NO-REPAIR-FOUND for the packet itself; partial upstream sequencing done.**

### F6 / N1 — duration-margins receipt consumer — **NOTHING CHANGED (authorization ≠ consumption)**

`git grep -ln "window_duration_margins_receipt" -- joulewise scripts` returns only
`joulewise/window_duration_margins.py` — still writer-side only, still no machine consumer, §11
ordering still unenforced. The one commit touching that module since the baseline is `00ec3b7`
(**PR #151, WO-MARGIN-RECORDER-AUTHZ**, on `origin/main`) — that cures **L4-B1**, the recorder's
*read* authorization for the governed spec (`TASK_QUEUE.md:105`), and does not give the receipt a
consumer. WO-L6-5's optional half is unexecuted. **NO-REPAIR-FOUND.**

### F7 / N2 — PRIVILEGE_INSTALLATION producer — **STILL NO PRODUCER; the safety condition still holds; D-127 landed as something else**

- The four rows are unchanged in `configs/arm_readiness/d117_row_registry_v1.json`:
  `privilege.activation_fence` / `.fresh_authorization` / `.installed_bytes` / `.isolated_interpreter`,
  each `"applicability_rule": "CLOCK_HELPER_ONLY"`, `"evaluation_phase": "ARM_ONLY"`,
  `"required_evidence_kinds": ["PRIVILEGE_INSTALLATION"]` (verified by parsing).
- `git grep -n "PRIVILEGE_INSTALLATION" -- joulewise scripts configs` finds the registry rows, the
  kind tables at `joulewise/arm_readiness.py:661,698,916-919`, and the fact-shape dict at `:811-822`
  — **no producer**. Only `tests/test_arm_readiness_registry.py:64-67` references them otherwise.
- **The safety condition still holds and is now hardcoded:** `scripts/capture_t0_step.py:438` emits
  `"clock_route": "MANUAL"`. The four rows therefore remain NOT_APPLICABLE.
- **What D-127 actually landed is NOT the helper route.** `scripts/joulewise-network-time.sudoers`
  now exists — "fixed network-time toggle capability for operator edr" — documented at
  `window_runbook.md:546-601,919`; `arm_readiness_evidence_t0.py:908` refuses if "fresh D-127
  enforcement did not set network time Off"; `prewindow_check.sh:102` notes clock state is
  deliberately not read there. The E-4 prior-state read is explicitly an **interactive Ed action with
  no repository script performing the privileged read** (`window_runbook.md:905-918`). So D-127
  widened *sudo for the toggle*, not the CLOCK_HELPER clock_route.

**NO-REPAIR-FOUND; the finding survives verbatim, its "harmless while MANUAL" premise intact.**

### F8 / N3 — arm-time horizon skip — **THE MECHANISM IS UNCHANGED**

Verified at HEAD by reading `joulewise/arm_readiness.py`:
- `_freeze_evidence_for_arm` (now at **`:5360`**, called from arm `:6139` and verify/consume `:6334`)
  passes `expected_boot_session_id`, and — new since the baseline — `expected_head_commit` and
  `lifecycle_registry`. It **still does not pass `now_monotonic_ns`.**
- The downstream defenses the finding named are all still present: the min-fold at `:6231-6252`
  (`"valid_until_monotonic_ns": valid_until` built from `min` over item horizons), verify refusal at
  `:6499` (`readiness_record_expired`, "arm receipt expired"), consumption checks at `:7126,7219,7910`.
- `_authenticate_generic_evidence_item` still *accepts* `now_monotonic_ns` (`:…` keyword-only) and
  still enforces it when supplied (`:4269-4277`, `:4486-4497`) — the caller simply doesn't supply it.

**NO-REPAIR-FOUND on the mechanism.** What changed is the *fact pattern*: the receipts are currently
unexpired (live probe above), so the "PASS rows from expired evidence" state is not presently
realizable — until the next 24 h lapse.

### Cross-cutting: work orders adjacent to this seam

| WO | State at HEAD | Citation |
|---|---|---|
| WO-KERNEL-RECONCILE | DONE — PR #150 `47d2645`, on `origin/main`; WINDOW-COUNCIL-GATE live; P2-006 retired (R3) | `TASK_QUEUE.md:104` |
| WO-MARGIN-RECORDER-AUTHZ | DONE — PR #151 `00ec3b7`, on `origin/main` | `TASK_QUEUE.md:105` |
| WO-T0-PRODUCER | DONE — PR #152 `a61ac92` + follow-up lane `65cc0f3`/`d8d2022`/`32cf987`, all on `origin/main` | `TASK_QUEUE.md:106` |
| WO-L2-REAUDIT | DONE — `0f886d3`, 251/251 enumerated | `TASK_QUEUE.md:102` |
| **WO-LAUNCH-BINDING** | **OPEN (A1, READY [AGENT])** — "Stages 1-3 MERGED (#156 `f392ff6`, #157 `bd333de`); calibration-side stage 2 DONE on the staged estimator branch @ `e22e658`…; **remaining: stage 4 successor flag inside the transaction. Launch stays NO-GO**" | `TASK_QUEUE.md:536,630`; stage checkpoint `TASK_QUEUE.md:491`; consult custody `docs/process_traces/2026-08-15-launcher-binding-consult/`, `2026-08-15-launch-f3-consult/`, `2026-08-16-launch-f3-coldgate/`, `2026-08-15-launch-lineage-consult/` |
| **WO-CONSUMPTION-EDGE** | **OPEN (A2, PARTIAL; READY [AGENT])** — "Code MERGED #155 (`d54db78`). … **Remaining before close: the production freeze (rides Phase 2) + the same-head production-pack L10 replay**" | `TASK_QUEUE.md:537,631`; custody `docs/process_traces/2026-08-15-consumption-edge-consult/` |
| WO-CENSUS-SEMANTICS | BLOCKED on ED-Q-L9-3 (that fixture is now captured — see §3) | `raw/CHANGE-UNIVERSE-BRIEF.md`; `TASK_QUEUE.md` current queue |
| WO-RECORDER-GRANT-IDENTITY | RETIRED WITHOUT IMPLEMENTATION by D-139 A1 | `TASK_QUEUE.md:101` |

---

## 3. ED-QUALIFICATION ROWS

### ED-QUAL-L6-1 (verbatim)

> ED-QUAL-L6-1 (stable capability, any tap block): execute the T-0 authoring path live on the measurement Mac — once the B1 capture helper exists, run the six E-step captures + clock attestation + launch manifest into arm_readiness.t0.inputs/ and author_arm_evidence_t0.py end-to-end under real passwordless-sudo powermetrics (POWERMETRICS_PROBE) and real systemsetup state (CLOCK_PROBE), confirming all 15 receipts author and a same-boot `generate_arm_readiness.py arm` reaches row evaluation. This lens could only prove the refusal side (P3) from the sandbox; the PASS side of the arm-plane producer seam needs Ed's machine and sudo.

Citation: `raw/L6-triage.md:58`; `sitting-packet-FINAL.md:176`.

**LOCATED CLOSURE EVIDENCE — PARTIAL. The row's own terminal condition is NOT met.**

*Precondition satisfied:* the B1 capture helper exists (§2, F1).

*Live, durable-receipt evidence located (all on the measurement Mac, Ed's hands, custody root
`~/JouleWise-window-custody/ed-qual-20260817/`, recorded at `docs/run_reports/2026-08-18-t10-session.md:100-112`
and `docs/process/ed-morning-packet-2026-08-18.md:112-125`):*

| Component | Result | Durable receipt |
|---|---|---|
| **D-127 sudoers install + exercise** | Installed `root:wheel 0440`; digest **`7dfe980b…`** verified; **both** vectors passwordless with ground-truth state flips (Network Time Off→On) | `sudoers-digest.txt`, `sudoers-vector-{on,off}.txt`, `vector-{on,off}-confirmed.txt`, `clock-{prior,post}-state.txt` |
| Sampler lifecycle (POWERMETRICS-adjacent) | PASS — cadence mean **1.0128 s**, zero orphans | `ed-session-evidence/sampler-checklist-*.log` (3 runs + plist) |
| ED-Q-L9-3 quiet census | Captured **23:51** with all agent runs quiesced; over-match findings confirmed as fixture ground truth | `quiet-census/` (6 files + `CAPTURE-NOTE.txt`) |
| ED-QUAL-L4-1 decisive replay | `DECISIVE REPLAY: OK`, 13,180.653 s, 23 proof selections | `decisive-replay.log` |
| Rail probe, backlight rows | executed; documentation-grade caveats recorded | `rail-probe-load-note.txt`, `keyboard-backlight.txt` |

*The terminal condition — the six live captures → `author_arm_evidence_t0.py` → 15 receipts →
same-boot `arm` reaching row evaluation — is the **dress rehearsal**, and it is recorded **OPEN**:*
- `docs/run_reports/2026-08-18-t10-session.md:110` — "| **Dress rehearsal** | **OPEN** — gated on the frozen `_v2` alpha pack, i.e. on Ed's item-1 ruling |"
- `docs/run_reports/2026-08-18-t10-session.md:13` — "Only the **dress rehearsal** remains"
- `docs/process/ed-morning-packet-2026-08-18.md:126` — "**OPEN: the dress rehearsal (item 4) only.**"
- The choreography is written and committed (`docs/process/rehearsal-operator-card.md`, full E-4→E-9
  + author→ARM→verify→consume + `launch_window.py`) but **targets the `_v2` pack**, while the live
  family is now `_v3` — so even the staged card is a family behind.
- **No later record of execution located.** `docs/run_reports/2026-08-19-t12-t13-session.md` contains
  **zero** matches for "rehearsal", "qualification", "prewindow", or "fiducial".

**NO closure evidence located for the row as written.** Searched:
`git grep -n "ED-QUAL-L6-1"` across `docs/` (→ zero hits outside the council trace);
`git grep -in "dress rehearsal"` across `RUN_STATE.md`, `docs/process`, `docs/run_reports`;
`docs/process/ed-morning-packet-2026-08-18.md`; `docs/process/ed-evening-checklist.md`;
`docs/process/ed-batch-packet.md`; `docs/phase_2/ed-qualification-session.md` (steps 1–6);
`docs/process/ed-s5-mint-decision-2026-08-19.md`; `docs/run_reports/2026-08-18-t10-session.md`;
`docs/run_reports/2026-08-19-t12-t13-session.md`; `docs/process_traces/2026-08-18-shakedown-first-light/`;
`docs/process_traces/2026-08-19-refreeze-execution/`; `RUN_STATE.md`.

### ED-QUAL-L6-2 (verbatim)

> ED-QUAL-L6-2 (stable capability, desk, no sudo but Ed's checkout): one full freeze-refresh rehearsal timed against the 24 h/same-boot coupling of B2 — re-author pack evidence, re-freeze, commit, dry-run, and measure the wall-clock of the lane so the window-day schedule in the WO2 runbook amendment is grounded in an observed duration, not an estimate.

Citation: `raw/L6-triage.md:60`; `sitting-packet-FINAL.md:177`.

**LOCATED CLOSURE EVIDENCE — the LANE WAS RUN TWICE FOR REAL, but the row's own deliverable (a
measured wall-clock) IS NOT LOCATED.**

*The lane executed, live, at Ed's measurement checkout `/Users/edr/JouleWise-measurement-20260818`:*
- **`_v2` / freeze-0002** — 2026-08-18, "freeze-0002 re-mints at the measurement checkout"
  (`docs/decision_log.md:166`, D-143); per-pack digests + freeze-receipt shas tabulated at
  `docs/process/ed-morning-packet-2026-08-18.md:95-97`.
- **`_v3` / freeze-0003** — 2026-08-19/20, three mints with PASS and explicit predecessor bindings:
  `5e38f1e`, `eb7f6c6`, `94dc3b3`, plus the S5 confirmation table `8b2b021`; U11 identity-pin
  projections `3d05982`, `6fd8bce`, `74632e3`. Ruling: D-147 (`docs/decision_log.md:170`), ONE home
  `docs/process_traces/2026-08-19-r1-r2-codesign/14-r2-ruling.md`. Execution custody:
  `docs/process_traces/2026-08-19-refreeze-execution/` (`r5-issuance/`, `r6-issuance/`, `reports/`,
  `s2-goldens/`, `s4/`, `suite-logs/`). **All BRANCH-ONLY.**
- Ed's own hands were required and used for the S5 mint route (D-148 cl.1; packet
  `docs/process/ed-s5-mint-decision-2026-08-19.md:33-50`).

*What is missing:* a recorded **wall-clock duration for the lane**, and the "window-day schedule in
the WO2 runbook amendment" that the duration was to ground. No WO-L6-2 runbook amendment naming a
timed freeze-refresh lane was located; the operative lane is instead the successor-pack transaction
(D-139 A3 / D-147), which is not scheduled in §4/§5C as a window-day step.

**NO closure evidence located for the timed measurement.** Searched:
`git grep -n "ED-QUAL-L6-2"` (zero hits outside the council trace);
`docs/process_traces/2026-08-19-refreeze-execution/` file listing; `docs/process/phase2-transaction-runsheet.md`
(referenced in the change brief); `docs/run_reports/2026-08-18-t10-session.md`;
`docs/run_reports/2026-08-19-t12-t13-session.md`; `docs/decision_log.md` D-139/D-143/D-147 bodies;
`docs/phase_2/window_runbook.md` §4/§5C for a named refresh lane with a duration.

---

## 4. CANDIDATE DISPOSITIONS FOR THE SEAT TO ADJUDICATE

**Candidate dispositions are assembled, not adjudicated; the seat rules.**

| Item | Candidate disposition | Exactly what remains / what is attached |
|---|---|---|
| **F1 / B1** T-0 input producer | **READY-evidence-attached** | Attached: `scripts/capture_t0_step.py` covering all nine inputs (PR #152 `a61ac92`, `origin/main`); runbook E-4…E-9b naming `arm_readiness.t0.inputs`; follow-up honest-contract lane landed (`65cc0f3`, `d8d2022`, `32cf987`, `origin/main`). Remains for the seat: whether a **trusted-operator ceremony interface** (fabrication explicitly undefended, D-148 cl.6 accepts it) discharges a finding whose scenario turned on operator-fabricated JSON; and whether the terminal-review remedy — a fail-closed **verifier** plus a **documented git ceremony**, with no Phase-3 pinning manifest — is the ordered producer. |
| **F2 / B2** freeze horizon + refresh lane | **STILL-OPEN** | Attached: successor-pack lane built and executed twice (`_v2`/freeze-0002, `_v3`/freeze-0003), freeze receipt v2 with predecessor chain, D-137/D-139 A3/D-140/D-141/D-147, live probe showing 33/33 receipts **unexpired with ~14.9 h headroom**. Remains: R1 lifecycle registry **not activated** (committed registry is v1, no `freeze_evidence_lifecycle`, D-148 cl.5 defers reserved values to council); evidence `head_commit` `1d3873b` is 28 commits stale and off `origin/main`; **Phase-3 baseline-manifest supersession not issued**; the 24 h re-run obligation is standing and unscheduled in §4/§5C. |
| **F3 / S2** stage-1 pin requirements | **STILL-OPEN — NO-REPAIR-FOUND** | Nothing changed. Neither WO-L6-4 branch taken (no committed `floor_mint_pin_requirements.v2`; no ruling of subsumption; no existence check in mint or close-out). |
| **F4 / S3** hashed backup receipts | **STILL-OPEN — NO-REPAIR-FOUND** | `scripts/backup_runs.sh` untouched across all 215 commits; no sha256, no receipt. §12 remains unperformable as written. **Note the ID collision: Disposition 4's struck "F4" is the L8 privilege-timing premise, not this item.** |
| **F5 / S4** FINAL arm packet stale | **STILL-OPEN — NO-REPAIR-FOUND** | Manifest still cites the 2026-08-13 packet. Successor packet correctly sequenced behind the end-to-end T-0 pass (not yet achieved) and must cite M-2 until the re-freeze retires it. Nearest artifact (`rehearsal-operator-card.md`) is self-declared non-claim evidence and targets `_v2`. |
| **F6 / N1** margins receipt has no consumer | **STILL-OPEN — NO-REPAIR-FOUND** | #151 cured the recorder's *read authorization* (L4-B1), not consumption. Schema still writer-only. |
| **F7 / N2** PRIVILEGE_INSTALLATION no producer | **STILL-OPEN — NO-REPAIR-FOUND** | Four rows unchanged (`CLOCK_HELPER_ONLY`/`ARM_ONLY`); no producer; `clock_route` hardcoded `MANUAL` at `capture_t0_step.py:438`, so the finding's own safety condition holds. D-127 landed a **network-time toggle** sudoers fragment, not the helper route. |
| **F8 / N3** arm-time horizon skip | **STILL-OPEN — NO-REPAIR-FOUND (mechanism)** | `_freeze_evidence_for_arm` (`:5360`) gained `expected_head_commit` + `lifecycle_registry` but still passes **no `now_monotonic_ns`**; min-fold + verify/consume remain the only defense. Fact pattern currently benign (receipts unexpired). Same seam as L7-F1, graded differently by the two seam readers. |
| **ED-QUAL-L6-1** | **ED-ROW OPEN** | D-127 sudoers + sampler + quiet census + decisive replay CLOSED with durable receipts in `~/JouleWise-window-custody/ed-qual-20260817/`. The row's terminal condition — live E-steps → author → 15 receipts → same-boot arm reaching row evaluation — is the **dress rehearsal, recorded OPEN**, and the staged card targets `_v2` not `_v3`. |
| **ED-QUAL-L6-2** | **ED-ROW OPEN (substantially exercised)** | The lane ran twice for real at the measurement checkout with durable freeze-0002/freeze-0003 receipts. **No measured wall-clock and no WO2 runbook amendment located** — the row's specific deliverable. |

---

## 5. WHAT A SKEPTICAL SEAT SHOULD PROBE

1. **[MANDATORY — zero-gap census re-run at the CURRENT head.]** L6's P1 census
   (`seat-reports/L6-SEAM-READER-A-report.md:63`: "all 35 rows have a producer route … The only kind
   with no producer anywhere is PRIVILEGE_INSTALLATION") was computed at `8937dec`. **215 commits have
   landed since, and they added producers and artifact kinds wholesale.** Re-run the census over
   `_DERIVERS`/`_ROW_KIND`/the registry JSON at `b92b43d`.
   *Falsifier:* any registry row, or any receipt kind reachable from the `_v3` packs, whose producer
   route is absent or is a test fixture. Immediate suspects: the four `privilege.*` rows (still
   producerless, currently N/A) and every kind introduced by WO-LAUNCH-BINDING.
2. **[MANDATORY — new artifact kinds with no consumer or no fail-closed refusal.]** Diffing
   `8937dec..HEAD` over `joulewise/` + `scripts/` yields **at least 29 schema IDs that did not exist
   in L6's 40-node universe**, including: `arm_readiness_freeze_receipt.v2`,
   `arm_readiness_row_registry.v2`, `arm_readiness_freeze_evidence_lifecycle_registry.v1`,
   `arm_readiness_freeze_predecessor_evidence_set.v1`, `arm_readiness_evidence_source.v2`,
   `arm_readiness_content_evidence_receipt.v1`, `arm_readiness_execution_evidence_receipt.v1`,
   `arm_readiness_execution_environment.v1`, `arm_readiness_launch_consumption.v1` **and** `.v2`,
   `launch_lineage.v1`, `launch_lineage_locator.v1`, `launch_start_receipt.v1`,
   `launch_settle_receipt.v1`, `launch_completion_receipt.v1`,
   `analysis_manifest_finalization.v1`, `analysis_semantics_projection.v1`,
   `calibration_bracket_binding.v1`, `calibration_observation_ledger.v1`,
   `detection_floor_artifact.v2`, `rehearsal_scratch_provenance.v1`,
   `idle_admission_evaluation_basis.v1`, `test_sampler_ack.v1`, the three
   `arm_readiness_t0_*` kinds. **The 40-node denominator is stale by construction.**
   *Falsifier:* any one of these with a producer and no machine consumer, or a consumer that does not
   fail closed on absence — the exact shape of N1, S3 and B1.
3. **[MANDATORY — is the terminal-review remedy CODE or a described intention?]** Read
   `scripts/capture_t0_step.py:288-317` and `joulewise/arm_readiness_evidence_t0.py:931-937`
   (verifiers, real, fail-closed) against `docs/phase_2/window_runbook.md:812-838` and
   `docs/process/rehearsal-operator-card.md:30` (the producer is a **human `git commit --allow-empty`
   ceremony**; no script creates it).
   *Falsifier for "delivered":* `git grep -l "allow-empty"` over `scripts/` finds no attestation
   producer; `docs/process/audit-baseline-manifest.json` names no attested commit — so the
   Addendum's "whose commit the superseding manifest pins" half is unbuilt. Also: the ordered step at
   `window_runbook.md:813` still says `cd /Users/edr/JouleWise-measurement-20260813` while the live
   checkout is `…-20260818` — run the step verbatim and it operates on the wrong tree.
4. **[MANDATORY — L6-vs-L7 divergence on the repaired seam.]** L6 graded the arm-time horizon skip a
   **nit** (defense one hop downstream); L7, executing, graded the same code a **should_fix** and
   added the live "33/33 already lapsed" fact. Neither grading changed; the code did not change; the
   *fact* did (receipts re-issued, now unexpired). Ask which lens's severity the repaired-state
   evidence vindicates, and whether re-issuance without enforcing the horizon at
   `_freeze_evidence_for_arm` is a cure or a reset of the clock.
   *Falsifier:* run `_freeze_evidence_for_arm` against a `_v3` pack after the current 14.9 h headroom
   lapses and observe whether FREEZE_AND_ARM rows report PASS from expired evidence.
5. **Re-run the live horizon probe at sitting time** (the numbers above are timestamped to assembly):
   `python3 -c "import time; print(time.monotonic_ns())"` against
   `min(valid_until_monotonic_ns)` over `configs/campaigns/d117_*_v3/arm_readiness.evidence/*.json`,
   plus `sysctl -n kern.bootsessionuuid` vs `da90818c-…`.
   *Falsifier:* headroom ≤ 0, or a boot-session change — either restores B2's original fact pattern
   and voids every freeze receipt on the branch.
6. **Probe whether the R1 lifecycle is live or dormant.** Parse
   `configs/arm_readiness/d117_row_registry_v1.json` for `schema_version` and a
   `freeze_evidence_lifecycle` key; then read `arm_readiness.py:5360-5395` for the
   `lifecycle_registry is None` path.
   *Falsifier for "R1 delivered":* registry is v1 with no lifecycle block ⇒ `expected_head` is `None`
   ⇒ the new head-binding and the `V1_GRANDFATHERING` refusal never fire on production packs; and
   D-148 cl.5 defers the registry's reserved values to a council that has not sat.
7. **Attack the `head_commit` binding.** All 33 `_v3` receipts bind `1d3873b`, 28 commits behind HEAD
   and absent from `origin/main`. Ask what an ARM at `b92b43d` binds, and whether the reviewed-head
   check (`reviewed_main`) can be satisfied at all while the whole Phase-2 transaction is branch-only.
   *Falsifier:* `git merge-base --is-ancestor 1d3873b origin/main` → exit 1 (confirmed at assembly).
8. **Test the three NO-REPAIR items cheaply and adversarially.**
   `git ls-files | grep -i pin_requirement` (expect empty ⇒ S2 stands);
   `grep -c sha256 scripts/backup_runs.sh` (expect 0 ⇒ S3 stands);
   `git grep -ln window_duration_margins_receipt -- joulewise scripts` (expect one writer-side file ⇒ N1 stands).
   *Falsifier for the assembler:* any non-empty result here means this row missed a repair.
9. **Press the ED-row terminal conditions.** Ask for the artifact that would close ED-QUAL-L6-1: a
   custody path containing fifteen T-0 receipts authored from wrapper-produced captures on the
   measurement Mac and a same-boot arm receipt reaching row evaluation, at the `_v3` family.
   *Falsifier:* the only rehearsal choreography committed
   (`docs/process/rehearsal-operator-card.md`) targets `_v2` and is recorded OPEN — so no such
   artifact can exist yet.
10. **Check whether closing WO-T0-PRODUCER moved the *charter* bar or only the *queue* bar.** The
    TASK_QUEUE row itself records "No phase exit-checklist matrix row exists" for every Phase-1 WO
    (`TASK_QUEUE.md:102-106`). Combined with `council-verdict.md:18-22`, a seat should ask what
    independent artifact — not the closing session's own report — certifies each closure.

---

## 6. OPEN ITEMS FROM THIS ROW

- **F3 / S2 — stage-1 `floor_mint_pin_requirements.v2`: NO REPAIR OF ANY KIND.** No committed
  instance, no subsumption ruling, no mint-side or close-out existence check. WO-L6-4 unexecuted in
  both of its permitted forms. Searched: `git ls-files | grep -i pin_requirement`,
  `git grep -n pin_requirements`, TASK_QUEUE completed + current queue, the should-fix batch commits.
- **F4 / S3 — hashed postcollection backup receipts: NO REPAIR.** `scripts/backup_runs.sh` has zero
  commits in the 215-commit span and contains no `sha256`. §12's two-root hashed-receipt obligation
  remains unperformable as written; WO-L6-5's primary half unexecuted.
- **F5 / S4 — the FINAL arm packet has not been regenerated**, and
  `docs/process/audit-baseline-manifest.json:3` still cites it. The successor packet is correctly
  sequenced behind an end-to-end T-0 pass that has not occurred; the nearest new document
  (`rehearsal-operator-card.md`) is self-declared non-claim evidence and is already one pack family
  stale (`_v2` vs live `_v3`).
- **F6 / N1 — the duration-margins receipt still has no machine consumer.** PR #151 authorized the
  recorder's read of the governed spec; it gave the receipt no consumer, and §11 ordering is still
  unenforced.
- **F7 / N2 — PRIVILEGE_INSTALLATION still has no producer anywhere in the repo**, and the only
  reason it is harmless is that `capture_t0_step.py:438` hardcodes `clock_route: MANUAL`. D-127
  landed a network-time **toggle** sudoers fragment, not the CLOCK_HELPER route — the finding's
  "any future arm context using the clock-helper route" hazard is untouched.
- **F8 / N3 — the arm-time horizon skip is unchanged in code.** `_freeze_evidence_for_arm`
  (`arm_readiness.py:5360`) still passes no `now_monotonic_ns`; the min-fold and verify/consume are
  still the sole defense. Only the fact pattern improved, and only for ~14.9 h from probe time.
- **The R1 freeze-evidence lifecycle exists in code but is DORMANT on production packs.** The
  committed registry is `joulewise.arm_readiness_row_registry.v1` with no `freeze_evidence_lifecycle`
  block, so `lifecycle_registry` and `expected_head_commit` are `None` at arm. D-148 cl.5 defers the
  R1 registry's reserved values to a council that has not sat.
- **Charter amendment-12 exposure is unresolved.** The re-freezes that cured B2's lapse are exactly
  the pack-byte changes that void the audit baseline, and the **Phase-3 superseding manifest with the
  ruled fields (`pack_digest_algorithm`, chain-template coverage note, paths for all bindings) has
  not been issued** (`council-verdict.md:68-70,102-104`).
- **The entire Phase-2 transaction — `_v3` packs, freeze-0003 ×3, U11 projections, D-146/D-147/D-148/D-149
  — is BRANCH-ONLY on `impl/r2-s0-mint-resolver` and absent from `origin/main` (`0099382`).** Every
  freeze-lane claim in this row depends on unmerged state.
- **The `_v3` evidence `head_commit` `1d3873b` is 28 commits behind HEAD and not on `origin/main`.**
- **`window_runbook.md:813` — the ordered terminal-review step still names the retired measurement
  checkout `/Users/edr/JouleWise-measurement-20260813`**, while the live checkout is
  `/Users/edr/JouleWise-measurement-20260818`. Run verbatim, the ordered step attests the wrong tree.
- **ED-QUAL-L6-1's terminal condition is not met:** the dress rehearsal (live E-steps → author → 15
  receipts → same-boot arm) is recorded **OPEN** at the latest record, and the committed rehearsal
  card targets `_v2`, not the live `_v3` family. No later execution record located.
- **ED-QUAL-L6-2's specific deliverable — a measured wall-clock for the freeze-refresh lane, and the
  WO2 runbook amendment it was to ground — IS NOT LOCATED**, despite the lane having been executed
  twice for real.
- **Neither ED row ID appears anywhere in the repository outside the 2026-08-15 council trace.**
  `git grep -n "ED-QUAL-L6-1\|ED-QUAL-L6-2"` over `docs/` returns zero hits elsewhere — there is no
  mechanical tracker binding these rows to closure evidence.
- **This seat's 34/40 coverage denominator was never adversarially tested**, and at least 29 new
  schema IDs have entered the chain since it was enumerated. Under `council-verdict.md:18-22` the
  denominator must be independently re-enumerated before any READY finding.
- **Five of L6's six unexecuted obligations remain unexecuted by this seat**, including the end-to-end
  CLI freeze/dry-run/arm/consume run and the open question handed to L2 (whether the
  `t0.ledger_reservation` predicate's `expected_plan_sha256` and the reservation's `FROZEN_PLAN` sha
  are the same identity). The R2 FROZEN_PLAN identity ruling (D-147, custody
  `docs/process_traces/2026-08-15-r2-frozen-plan-consult/` and
  `2026-08-19-r1-r2-codesign/14-r2-ruling.md`) may have answered it; **this assembler did not verify
  that it does**, and the seat should not assume it.
- **Packet-metadata discrepancies to correct on the record:** the assembler brief names HEAD
  `4597ad4`/`d10881b` and "214 commits", while the tree is at `b92b43d` with **215** commits from
  `8937dec`.
