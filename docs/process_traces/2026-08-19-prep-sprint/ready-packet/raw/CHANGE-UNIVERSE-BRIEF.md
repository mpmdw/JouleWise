# CHANGE-UNIVERSE BRIEF (shared input to row assemblers)

Read-only tree: `/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtS0`
Branch `impl/r2-s0-mint-resolver`, HEAD **4597ad4**. Council audit baseline: **8937dec**
(manifest head ac3fe1d + three files). **214 commits** separate them
(`raw/commits-since-baseline.txt`).

## Where "what changed" lives

- **Run reports** (session narratives, dispositions): `docs/run_reports/2026-08-15-t8-session.md`
  (council sitting), `2026-08-16-t9-session.md` (**Phase 1 code wave**),
  `2026-08-18-t10-session.md` (Phase 2 transaction start + shakedown first light),
  `2026-08-19-t12-t13-session.md` (S0–S5, r6, stop orders).
- **TASK_QUEUE.md**: completed WO rows at lines 102–110 carry PR numbers + merge SHAs +
  delivered-evidence text. Per-WO detail sections at lines ~193–500. Current queue from line 502.
  `## Active Global Work-Selection Gates` (line 587) holds `WINDOW-COUNCIL-GATE` and the
  [ED-EXTERNAL] / [QUIET-MAC] / [AGENT] lanes.
- **Kernel**: `docs/process/state_kernel.json` (gates, tasks, latest_report, authority).
- **Decision log**: `docs/decision_log.md` — D-137 (arm-readiness monotonic expiry bound to boot
  session), D-138 (detection budget merge-staging), D-139 (Ed A1–A3 rulings), D-140/D-141
  (freeze-status byte semantics; generator write-boundary residuals), D-142, D-143 (165k budget),
  D-144 (co-design protocol), D-145, D-146 (**R1 ruling** — production capture-pipeline v3),
  D-147 (**R2 ruling** — mint-lane fan-out composite), D-148 (Ed's seven rulings 2026-08-19),
  D-149 (standing conditional T-0 GO / no-hands window automation).
- **Process traces created since the council** (custody homes for repairs/rulings):
  `2026-08-15-l2-reaudit`, `-consumption-edge-consult`, `-launch-f3-consult`,
  `-launch-lineage-consult`, `-launcher-binding-consult`, `-m2-coldgate`,
  `-r1-freeze-lifecycle-consult`, `-r2-frozen-plan-consult`, `-recorder-authz-consult`,
  `-recorder-race-coldgate`, `-t0-capture-provenance-consult`;
  `2026-08-16-grant-identity-consult`, `-launch-f3-coldgate`, `-phase2-plan-consult`;
  `2026-08-17-freeze-numbering-consult`; `2026-08-18-anchor-v3-science-review`,
  `-freeze-semantics-coldgate`, `-shakedown-first-light`, `-t10-t11-working-notes`;
  `2026-08-19-r1-r2-codesign` (16 files incl. `13-r1-ruling.md`, `14-r2-ruling.md`,
  `15-amendment-r6.md`, `16-d144-seatpass-packet.md`), `2026-08-19-refreeze-execution`
  (subdirs `r5-issuance/`, `r6-issuance/`, `reports/`, `s2-goldens/`, `s4/`, `suite-logs/`).
- **Ed-facing operator artifacts**: `docs/phase_2/ed-qualification-session.md` (6 steps),
  `docs/process/ed-batch-packet.md`, `docs/process/ed-evening-checklist.md`,
  `docs/process/ed-morning-packet-2026-08-18.md`, `docs/process/rehearsal-operator-card.md`,
  `docs/process/d149-go-receipt-template.md`, `docs/process/phase2-transaction-runsheet.md`,
  `docs/process/ed-s5-mint-decision-2026-08-19.md`, `scripts/ed_session/{sampler-checklist.sh,
  rail-probe.sh,build_rehearsal_env.sh}`.
- **Status surfaces**: `RUN_STATE.md`, `WINDOW_STATUS.md`, `CLAIMS_STATUS.md`, `PROJECT_STATUS.md`,
  `README.md`, `docs/phase_2/phase_2_exit_checklist.md`, `docs/council_log.md`.

## Council program phases to check delivery against

- Phase 0 rulings: R1 freeze-evidence lifecycle, R2 FROZEN_PLAN identity, R3 P2-006 retirement,
  R4 M-2 execution-note amendment + remanded M-2 cold gate; design consults for the
  prospective-manifest validator/finalizer and margin-recorder authorization; L8-B7 launcher
  binding as contract-bearing.
- Phase 1 WOs: WO-KERNEL-RECONCILE · WO-T0-PRODUCER · WO-LAUNCH-BINDING · WO-CONSUMPTION-EDGE ·
  WO-MARGIN-RECORDER-AUTHZ · WO-CENSUS-SEMANTICS (gated on ED-Q-L9-3) · WO-DETECT-PULSES-BUDGET ·
  WO-L2-REAUDIT · should-fix batch (sweep B1/B2/B3/B6/B7 + D-130 disposition) + L11's three paper
  corrections.
- Ed-required batched session (see council-verdict.md lines 89–95).
- Phase 2: atomic re-freeze LAST among pack-byte changes; then successor arm packet.
- Phase 3: baseline-manifest SUPERSESSION + focused re-audit (L1, L5, L7 minimum) + adversarial
  coverage re-enumeration of ALL universes; C-028 delta re-audits on every fix round.
- Phase 4: reconvened READY-CANDIDATE sitting with fresh cold pairing.

## Standing caution for assemblers

The verdict states (lines 18–22) that **the work-order program is NOT CERTIFIED COMPLETE**: every
seat's evidence universe was self-nominated and the one denominator adversarially tested fell.
Closing a work order therefore does not by itself entitle a READY disposition — that is exactly
what the seats must adjudicate. Assemble evidence; do not grade.
