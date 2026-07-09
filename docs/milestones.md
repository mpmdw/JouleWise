# Milestones And Calendar Map

Status: skeleton - real dates pending user input (task P1-008). Capstones
fail by calendar, not by code (R-012); this file exists so schedule risk is
visible in one place. Update dates the moment they are known; review at
every phase start.

## Known Date Constraints

| Constraint | Date | Source |
|---|---|---|
| Mac local-machine auth session (unblocks privileged powermetrics sample) | CLOSED 2026-07-06 - privileged sample captured and sudoers rule recorded (C-027 correction: this row had stayed "to reschedule" after the gate closed; the missed 2026-06-10 slot remains a historical note) | user; updated 2026-07-09 |
| Project pause (vacation) | 2026-06-13 through 2026-07-04 | user; recorded 2026-07-05 so the run-report gap reads as planned, not stalled |
| Supervisor approval meeting | TBD | P1-001 |
| 3080 Ti borrow window | TBD | R-006; needed during Phase 3 Stage 3.4 |
| Colloquium date | TBD | user/program |
| Final report due | TBD | user/program |

## Evidence-By Dates (C-027 / proposed D-060)

Every external gate needs a hard evidence-by date with an automatic cut
rule: if the gate is not proven by its date, the project moves
permanently to the Mac + synthetic-transfer/analytical-composition
floor for that dependency. Dates to be filled with P1-008. The automatic cut rule TAKES EFFECT
only if/when Ed ratifies D-060 (currently PROPOSED); it is recorded
now so the schedule risk and the intended mechanism are visible.

## Phase Targets

Fill "Target end" from the real deadlines backwards once known. Until
then, the dependency structure is the schedule.

| Phase | Depends on | Hardware-critical window | Target end |
|---|---|---|---|
| 1: Approval, feasibility, measurement design | supervisor + device access | local auth session CLOSED 2026-07-06; lab answers | TBD |
| 2: Harness + Mac slice + baselines | Phase 1 readiness gate | Mac sessions; remote-node access | TBD |
| 3: Disaggregation + interconnect sweep | Phase 2 readiness gate | borrow window; network hardware | TBD |
| 4: Analysis | dataset frozen | none (desk work) | TBD |
| 5: Presentation + submission | Phase 4 gate | rehearsals, supervisor review | TBD |

## Scheduling Rules

- Hardware-gated work is scheduled around access windows; desk work
  (hardware-independent floors listed in each phase plan) fills the gaps -
  no idle time while blocked.
- The borrow window (R-006) must land after Stage 3.0 verdicts and the
  rehearsed runbook exist; if it cannot, the GPU<->GPU pairing is descoped
  per the ladder rather than rushed.
- Phase 4 needs no hardware: it is the schedule buffer. If dates compress,
  protect Phase 2's Mac slice and Phase 3's synthetic sweep first (the
  R-012 floor), and shrink Phase 3's matrix before shrinking Phase 4's
  audit rigor.
- Slides (5.4) want frozen figures >=1 week before the colloquium;
  the report (5.5) wants the claims-index final pass >=1 week before
  submission. Work backwards from there when dates land.
- Heartbeat (added 2026-07-05): if more than 14 days pass with no run
  report and no recorded break in this file, the next session starts with
  a milestones + risk-register review before any other work - a
  calendar-risk-dominated project must notice its own silence. Planned
  breaks are recorded in the constraints table above so they do not
  trip this rule.
